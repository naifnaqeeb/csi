import argparse
import os
import re
import sys
from termcolor import colored

def grep(pattern, files, recursive=False, ignore_case=False, invert_match=False,
         whole_word=False, colorize=False, context_lines=0, count_only=False,
         include=None, exclude=None):
    matching_lines_count = 0

    if ignore_case:
        pattern_compiled = re.compile(pattern, re.IGNORECASE)
    else:
        pattern_compiled = re.compile(pattern)

    for file_path in files:
        if os.path.isdir(file_path):
            if recursive:
                for root, _, filenames in os.walk(file_path):
                    for filename in filenames:
                        if include and not any(re.match(i, filename) for i in include):
                            continue
                        if exclude and any(re.match(e, filename) for e in exclude):
                            continue
                        grep_in_file(os.path.join(root, filename), pattern_compiled, ignore_case,
                                     invert_match, whole_word, colorize, context_lines, count_only)
            else:
                print(f"{file_path}: Is a directory")
        else:
            grep_in_file(file_path, pattern_compiled, ignore_case, invert_match,
                         whole_word, colorize, context_lines, count_only)
            matching_lines_count += grep_in_file(file_path, pattern_compiled, ignore_case, invert_match,
                         whole_word, colorize, context_lines, count_only)

    if count_only:
        print("Total matching lines count:", matching_lines_count)

def grep_in_file(file_path, pattern_compiled, ignore_case, invert_match, whole_word,
                 colorize, context_lines, count_only):
    matching_lines_count = 0
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            for i, line in enumerate(lines):
                match = pattern_compiled.search(line)
                if (match and not invert_match) or (not match and invert_match):
                    matching_lines_count += 1
                    if count_only:
                        continue

                    if colorize:
                        line = colorize_matched_text(line, match)

                    if context_lines > 0:
                        print_context_lines(lines, i, context_lines)

                    print_line(file_path, i + 1, line)
    except IOError:
        print(f"Error: Unable to read file {file_path}")

    return matching_lines_count

def colorize_matched_text(line, match):
    matched_text = match.group(0)
    start_index = line.find(matched_text)
    end_index = start_index + len(matched_text)
    return line[:start_index] + colored(matched_text, 'red') + line[end_index:]

def print_context_lines(lines, current_index, context_lines):
    start_index = max(0, current_index - context_lines)
    end_index = min(len(lines), current_index + context_lines + 1)
    for i in range(start_index, end_index):
        print(lines[i], end='')

def print_line(file_path, line_number, line):
    print(f"{file_path}:{line_number}:{line}", end='')

def main():
    parser = argparse.ArgumentParser(description='grep-like utility in Python')
    parser.add_argument('pattern', help='pattern to search for')
    parser.add_argument('files', nargs='+', help='files to search in')
    parser.add_argument('-r', '--recursive', action='store_true', help='recursively search through directories')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='ignore case distinctions')
    parser.add_argument('-v', '--invert-match', action='store_true', help='select non-matching lines')
    parser.add_argument('-w', '--whole-word', action='store_true', help='match whole words only')
    parser.add_argument('-c', '--count-only', action='store_true', help='print only a count of matching lines per file')
    parser.add_argument('--colorize', action='store_true', help='highlight matching text in color')
    parser.add_argument('-C', '--context-lines', type=int, default=0, help='display specified number of lines before and after each matching line')
    parser.add_argument('--include', nargs='*', help='include only files matching these patterns')
    parser.add_argument('--exclude', nargs='*', help='exclude files matching these patterns')

    args = parser.parse_args()

    grep(args.pattern, args.files, args.recursive, args.ignore_case, args.invert_match,
         args.whole_word, args.colorize, args.context_lines, args.count_only,
         args.include, args.exclude)

if __name__ == '__main__':
    main()
