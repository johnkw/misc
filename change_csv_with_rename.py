import csv, write_with_rename

def perform(filepath, callback, dialect=csv.excel_tab, callback_args=[], callback_vargs={}):
    reader = csv.DictReader(open(filepath,'r'), dialect=dialect)
    with write_with_rename.WriteWithRename(filepath) as f:
        writer = csv.DictWriter(f, reader.fieldnames, dialect=dialect)
        writer.writeheader()
        for row in callback(reader, *callback_args, **callback_vargs):
            writer.writerow(row)
