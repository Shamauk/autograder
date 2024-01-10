from flask import Flask, request, jsonify, abort
import os
import json
import hashlib
import docker
import time

app = Flask(__name__)
SUBMISSIONS_DIR = "submissions"
IMAGES_DIR = "images"
TEST_DIR = "tests"
ASSIGNMENTS_FILE = "assignments.json"
GRADING_FILE = "grading.json"
PORT = 5035

ACCEPTED_FILE_TYPES = [
    "zip", "tar", "tar.gz",
]

def read_assignments():
    with open(ASSIGNMENTS_FILE) as file:
        return json.load(file)
    
def read_grading(dir):
    with open(os.path.join(dir, GRADING_FILE)) as file:
        return json.load(file)

@app.route('/submit/<assignment_name>/<student_id>', methods=['POST'])
def submit_assignment(assignment_name, student_id):
    assignments = read_assignments()

    if assignment_name not in assignments or not assignments[assignment_name]["visible"]:
        abort(404, description="Assignment not found or not visible.")

    if 'file' not in request.files:
        abort(400, description="No file part.")

    file = request.files['file']
    if file.filename == '':
        abort(400, description="No selected file.")
    
    if file:
        # Extract the file extension
        file_extension = file.filename[file.filename.find("."):]
        if file_extension[1:] not in ACCEPTED_FILE_TYPES:
            abort(400, description="File type not accepted.")

        # Use student_id as the filename and append the file extension
        filename_noextension = f"{student_id}"
        filename = f"{filename_noextension}{file_extension}"

        assignment_path = os.path.join(SUBMISSIONS_DIR, assignment_name)
        os.makedirs(assignment_path, exist_ok=True)
        filepath = os.path.join(assignment_path, filename)
        filepath_noextension = os.path.join(assignment_path, filename_noextension)
        file.save(filepath)

        os.system(f"rm -rf {filepath_noextension}")
        os.system(f"mkdir {filepath_noextension}")
        if file_extension == ".zip":
            os.system(f"unzip {filepath} -d {filepath_noextension}")
        elif file_extension == ".tar":
            os.system(f"tar -xf {filepath} -C {filepath_noextension}")
        elif file_extension == ".tar.gz":
            os.system(f"tar -xzf {filepath} -C {filepath_noextension}")
        else:
            abort(400, description="File type not accepted.")
        contents = os.listdir(filepath_noextension)
        if len(contents) == 1 and os.path.isdir(os.path.join(filepath_noextension, contents[0])):
            os.system(f"mv {os.path.join(filepath_noextension, contents[0])}/* {filepath_noextension}")
            os.system(f"rm -rf {os.path.join(filepath_noextension, contents[0])}")

        create_docker_image(assignment_name)
        result = run_tests(assignment_name, filepath_noextension)

        return jsonify(message=f"Autograded with performance {result}"), 200

    return jsonify(message="File upload failed."), 400

def create_docker_image(assignment_name):
    client = docker.from_env()
    image_path = os.path.join(IMAGES_DIR, assignment_name)
    if not os.path.exists(image_path):
        abort(404, description="Assignment docker image not found.")
    
    with open(image_path, "rb") as file:
        current_hash = hashlib.sha256(file.read()).hexdigest()
    
    try:
        image = client.images.get(assignment_name)
        if image.labels.get("hash") != current_hash:
            image = client.images.build(path=IMAGES_DIR, dockerfile=assignment_name, tag=assignment_name, labels={"hash": current_hash})
    except docker.errors.ImageNotFound:
        image = client.images.build(path=IMAGES_DIR, dockerfile=assignment_name, tag=assignment_name, labels={"hash": current_hash})
    
    return image

def run_tests(assignment_name, src_file_path):
    results = ""

    assignments = read_assignments()
    assignment = assignments[assignment_name]
    assignment_test_dir = os.path.join(TEST_DIR, assignment_name)
    if not os.path.exists(assignment_test_dir):
        abort(404, description="Test directory not found.")
    grading = read_grading(assignment_test_dir)

    if not assignment["visible"]:
        abort(404, description="Assignment not found or not visible.")

    result = 0
    num_tests = len(grading)
    for index, test_name in enumerate(grading):
        test_file_path = os.path.join(assignment_test_dir, test_name)
        if not os.path.exists(test_file_path):
            abort(404, description="Test not found.")
        points, info = run_test(assignment_name, grading[test_name], src_file_path, test_file_path, test_name)
        info = info.strip().replace("\n", " ")
        result += points
        results += f"({index+1}/{num_tests}) {test_name}: {info} ({points} points)\n"
    
    open(os.path.join(src_file_path, "results.json"), "w").write(results)
    return result

def run_test(assignment_name, config, src_file_path, test_file_path, test_name):
    client = docker.from_env()
    container = None

    # Convert relative paths to absolute paths
    src_file_path = os.path.abspath(src_file_path)
    test_file_path = os.path.abspath(test_file_path)

    try:
        container = client.containers.create(assignment_name, volumes={
            src_file_path: {
                "bind": "/src",
                "mode": "ro"
            },
            test_file_path: {
                "bind": f"/{test_name}",
                "mode": "ro"
            }
        }, command='/bin/bash', tty=True, detach=True)


        container.start()

        while True:
            # Reload the container object to get the current status
            container.reload()

            if container.status == "running":
                break
            elif container.status != "created":
                print(container.status)
                abort(500, description="Failed to start container.")
            
            time.sleep(1)

        if "compile" in config:
            exit_code, output = container.exec_run(config["compile"])
            if exit_code != 0:
                abort(400, description=output)

        if "exec" in config:
            exit_code, output = container.exec_run(config["exec"])
            if exit_code != 0:
                return 0, output.decode()
            else:
                return config["points"], output.decode()
    except docker.errors.ImageNotFound:
        abort(404, description="Assignment docker image not found.")
    finally:
        if container:
            container.stop()
            container.remove()

    return 0



if __name__ == '__main__':
    app.run(debug=True, port=PORT)