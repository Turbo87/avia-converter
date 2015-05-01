#!/usr/bin/env python

import argparse
import csv
import sys

UNKNOWN_VALUE = ''


def read(input):
    reader = csv.DictReader(input, delimiter=';')
    for row in reader:
        if row['Lfz.'] is None:
            continue

        del row['']
        yield row


def convert(row, members):
    result = []

    lfz = row['Lfz.'].split('-')
    if len(lfz) > 1:
        landeskennung = lfz[0]
        kennzeichen = lfz[1]
    else:
        landeskennung = ''
        kennzeichen = lfz[0]

    # Landeskennung
    result.append(landeskennung)

    # Kennzeichen
    result.append(kennzeichen)

    # Datum
    result.append(row['Datum'])

    # Startzeit
    result.append(row['Start'])

    # Landezeit
    result.append(row['Landung'])

    # Flugzeit
    result.append(row['Zeit'])

    # Startort
    result.append(row['Startort'])

    # Landeort
    result.append(row['Landeort'])

    # Anzahl Landungen
    result.append(row['Landungen'])

    # Ausland
    result.append('F')

    # Preiskategorie
    preiskategorie = 'X' if row['Abr.'] == 'K' else ''
    result.append(preiskategorie)

    # PIC1
    result.append('T')

    # Besatzung1
    pilot = members.get(row['Pilot'], UNKNOWN_VALUE)
    if pilot != UNKNOWN_VALUE:
        pilot = pilot['Mitgliedsnr']

    result.append(pilot)

    # Anteil_1
    result.append(UNKNOWN_VALUE)

    # Besatzung2 ('Begleiter/FI' has copilot name, not ID)
    copilot = members.get(row['Begleiter/FI'], UNKNOWN_VALUE)
    if copilot != UNKNOWN_VALUE:
        copilot = copilot['Mitgliedsnr']

    result.append(copilot)

    # Anteil_2
    result.append(UNKNOWN_VALUE)

    # Besatzung3
    result.append(UNKNOWN_VALUE)

    # Anteil_3
    result.append(UNKNOWN_VALUE)

    # Besatzung4
    result.append(UNKNOWN_VALUE)

    # Anteil_4
    result.append(UNKNOWN_VALUE)

    # Bemerkung
    result.append(row['Bemerkung'])

    # Hoehenmeter
    result.append(row['Schlepph\xf6he'])

    # Einheiten
    result.append(UNKNOWN_VALUE)

    # Leistung1
    result.append(UNKNOWN_VALUE)

    # VLS1PK
    result.append(UNKNOWN_VALUE)

    # Leistung2
    result.append(UNKNOWN_VALUE)

    # VLS2PK
    result.append(UNKNOWN_VALUE)

    # Flugart
    result.append(row['Flugart'])

    # Startart
    result.append(row['S.-Art'])

    # Luftfahrzeugart
    if row['Lfz.'].startswith('D-E'):
        lfz_art = 1
    elif row['Lfz.'].startswith('D-K'):
        lfz_art = 3
    elif row['Lfz.'].startswith('D-'):
        lfz_art = 2
    else:
        lfz_art = UNKNOWN_VALUE

    result.append(lfz_art)

    return result


def read_members(fp):
    members = {}

    for row in csv.DictReader(fp, delimiter=';'):
        name = row['Nachname'] + ', ' + row['Vorname']
        members[name] = row

    return members


def main(input, members, output):
    members = read_members(members)

    writer = csv.writer(output, delimiter=';')
    for row in read(input):
        writer.writerow(convert(row, members))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert flight logs from vereinsflieger.de CSV to ameavia CSV.')
    parser.add_argument('input', type=file, help='the exported vereinsflieger.de CSV')
    parser.add_argument('members', type=file, help='the exported ameavia club member list as CSV')
    parser.add_argument('--output', '-o', help='filename for the generated output')
    args = parser.parse_args()

    if args.output:
        output = open(args.output, 'w')
    else:
        output = sys.stdout

    main(args.input, args.members, output)
