import os
import xml.etree.ElementTree as ET
import hashlib

def hash_file(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def find_failures(root):
    failures = []
    for testsuite in root.findall('testsuite'):
        for testcase in testsuite.findall('testcase'):
            failure = testcase.find('failure')
            if failure is not None:
                failures.append({
                    'testcase': testcase.attrib['name'],
                    'testsuite': testsuite.attrib['name'],
                    'message': failure.attrib['message']
                })
    return failures

def normalize_xml(file):
    tree = ET.parse(file)
    root = tree.getroot()

    for elem in root.iter():
        if 'timestamp' in elem.attrib:
            del elem.attrib['timestamp']
        if 'time' in elem.attrib:
            del elem.attrib['time']
        if 'id' in elem.attrib:
            del elem.attrib['id']

    return ET.tostring(root, encoding='utf-8')

def xml_files_identical(file1, file2):
    norm1 = normalize_xml(file1)
    norm2 = normalize_xml(file2)
    
    return norm1 == norm2

def compare_files(file1, file2):
    trees = [ET.parse(file1), ET.parse(file2)]
    roots = [tree.getroot() for tree in trees]

    all_failures = [find_failures(root) for root in roots]

    result = []

    for idx, (file, failures) in enumerate(zip([file1, file2], all_failures)):
        file_name = os.path.basename(file)
        file_index = idx + 1
        result.append(f"File {file_index} - Test Failures in {file_name}:")
        if failures:
            for failure in failures:
                result.append(f"  Test Suite - {failure['testsuite']}")
                result.append(f"  Test Case - {failure['testcase']}")
                result.append(f"  Failure Message - {failure['message']}\n")
        else:
            result.append("  No failures.\n")

    if xml_files_identical(file1, file2):
        result.append(f"\nThe files {os.path.basename(file1)} and {os.path.basename(file2)} are identical.\n")

    return "\n".join(result)

if __name__ == "__main__":
    if 'XML_FILE1' in os.environ and 'XML_FILE2' in os.environ:
        file1 = os.getenv('XML_FILE1')
        file2 = os.getenv('XML_FILE2')

        comparison_result = compare_files(file1, file2)
        with open("SampleArtifact/comparison_output.txt", "w") as output_file:
            output_file.write(comparison_result)
    else:
        print("Environment variables XML_FILE1 and XML_FILE2 are not set.")
