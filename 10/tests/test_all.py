import os
import sys
import subprocess
import string

evolution_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..%s" % os.sep)
sys.path.append(evolution_path)

if __name__ == '__main__':
    files = os.listdir(os.getcwd())
    for i in sorted(files):
        if i.endswith("in.json"):
            print("--------  " + i + "  --------")
            file = open(i)
            p1 = subprocess.Popen(["./xstep", ""], stdin=file, stdout=subprocess.PIPE, cwd=os.path.relpath(".."))
            result = p1.stdout.read()
            result = result.translate(None, string.whitespace)
            output,err = p1.communicate()
            outfile_name = i.replace("in.json", "out.json")
            expected = open(outfile_name).read()
            expected = expected.translate(None, string.whitespace)
            if (result == expected):
                print("The test passed! \n")
            else:
                print("The test FAILED.\n")
                print("Expected:\n" + expected)
                print("Actual:\n" + result)
