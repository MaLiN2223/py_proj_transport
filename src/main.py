import sys
import configparser

def entrypoint():
    config = configparser.ConfigParser()



def main():
        try:
            entrypoint()
        except Exception as e:
            print("{0}, message : {1}".format(sys.stderr,e))
            return 2

if __name__ == "__main__":
    sys.exit(main())