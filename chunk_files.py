import os

class Process:

    def __init__(self) -> None:
        #init objects
        self.n_lines = 0

    def _process_wrapper(self, chunkStart, chunkSize, file, encoding, func):
        with open(file, encoding=encoding) as f:
            f.seek(chunkStart)
            lines = f.read(chunkSize).splitlines()
            self.n_lines += len(lines)
            for n, line in enumerate(lines):
                line = line.rstrip('\n')
                func(line)
                if n == len(lines) - 3:
                    breakpoint

    def _chunkify(self, file, encoding, size=1024*1024):
        fileEnd = os.path.getsize(file)
        with open(file, 'rb') as f:
            chunkEnd = f.tell()
            while True:
                chunkStart = chunkEnd
                f.seek(size, 1)
                f.readline()
                chunkEnd = f.tell()
                yield chunkStart, chunkEnd - chunkStart
                if chunkEnd > fileEnd:
                    break

    def process(self, file, func, encoding='utf-8', max_lines=None):
        for chunkStart, chunkSize in self._chunkify(file, encoding):
            self._process_wrapper(chunkStart, chunkSize, file, encoding, func)
            
            if max_lines:
                print(f'{round((self.n_lines / max_lines)*100, 2)}% processat, ({self.n_lines} utav {max_lines} antal rader)')
