import time
import re

class LogFileReader(object):
    def __init__(self, fn):
        self.fn = fn
        self.lastline = None
    
    def get_new_lines(self):
        # read the last line of the file
        with open(self.fn, 'r') as f:
            lines = f.readlines()
        
        for (i, l) in enumerate(lines):
            if l == self.lastline:
                lines = lines[i+1:]
                break
        
        if len(lines) > 0:
            self.lastline = lines[-1]
        
        return lines
    
    def clear_lines(self):
        with open(self.fn, 'r') as f:
            lines = f.readlines()
        
        if len(lines) == 0:
            self.lastline = None
        else:
            self.lastline = lines[-1]
    
    def __call__(self):
        while True:
            for line in self.get_new_lines():
                self.parse(line)
            
            time.sleep(1)
    
    def parse(self, line):
        raise NotImplementedError


class DNSReader(LogFileReader):
    REGEX = re.compile(r"(.*)query\[A+\]\s(.+)\sfrom\s(.+)")

    def __match(self, line):
        match = DNSReader.REGEX.match(line)
        if match is not None:
            return (match.group(2), match.group(3).strip())
        else:
            return (None, None)

    def parse(self, line):
        (domain, src) = self.__match(line)

        if domain is not None:
            self.handle(domain, src)

    def parse_new_lines(self):
        lines = []

        for l in self.get_new_lines():
            (a, b) = self.__match(l)
            if a is not None:
                lines.append((a, b))

        return lines
            
if __name__ == "__main__":
    
    class ExampleThing(DNSReader):
        def __init__(self):
            super().__init__("/root/app-log")
        def handle(self, domain, src):
            print("query for {} from {}".format(domain, src))
    
    reader = ExampleThing()
    reader.clear_lines()
    reader()