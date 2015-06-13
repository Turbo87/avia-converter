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
    if row['Abr.'] == 'K':
        preiskategorie = 'X'

    elif row['Flugart'] in ('C', 'S', 'N'):
        preiskategorie = 'C'

    elif row['Flugart'] == 'P':
        preiskategorie = 'G'

    elif row['Flugart'] == 'W':
        preiskategorie = 'X'

    else:
        preiskategorie = ''

    result.append(preiskategorie)

    # PIC1
    result.append('T')

    # Besatzung1
    pilot = members.get(row['Pilot'], UNKNOWN_VALUE)
    if pilot != UNKNOWN_VALUE:
        pilot = pilot['Mitgliedsnr']

    result.append(pilot)

    # Anteil_1
    if row['Abr.'] == 'P':
        anteil1 = 100
    elif row['Abr.'] == 'PB':
        anteil1 = 50
    else:
        anteil1 = 0

    result.append(anteil1)

    # Besatzung2 ('Begleiter/FI' has copilot name, not ID)
    copilot = members.get(row['Begleiter/FI'], UNKNOWN_VALUE)
    if copilot != UNKNOWN_VALUE:
        copilot = copilot['Mitgliedsnr']

    result.append(copilot)

    # Anteil_2
    if row['Abr.'] == 'B':
        anteil2 = 100
    elif row['Abr.'] == 'PB':
        anteil2 = 50
    else:
        anteil2 = 0

    result.append(anteil2)

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
    motor_start = row['M.-Start']
    motor_ende = row['M.-Ende']

    if motor_start and motor_ende:
        motor_start = float(motor_start.replace(',', '.'))
        motor_ende = float(motor_ende.replace(',', '.'))
        result.append(('%.2f' % (motor_ende - motor_start)).replace('.', ','))
    else:
        result.append(UNKNOWN_VALUE)

    ohne_marke = ('ohne marke' in row['Bemerkung'].lower() or 'keine marke' in row['Bemerkung'].lower())
    own_tug_plane = row['Schlepp-Lfz'] in ('D-EFAC', 'D-KUFP')

    pilot = members.get(row['Pilot'])
    if pilot:
        is_student = pilot['Kostenstufe'] == 'Jugendlicher'
    else:
        is_student = False

    # Leistung1
    leistung1 = UNKNOWN_VALUE
    if own_tug_plane:
        if ohne_marke and row['Schlepph\xf6he'] in ('600', '1000'):
            leistung1 = 'FSS6' if is_student else 'FSV6'
        elif not ohne_marke and row['Schlepph\xf6he'] == '1000':
            leistung1 = 'FSSZ' if is_student else 'FSVZ'

    result.append(leistung1)

    # VLS1PK
    result.append('T' if leistung1 else UNKNOWN_VALUE)

    # Leistung2
    leistung2 = UNKNOWN_VALUE
    if own_tug_plane:
        if ohne_marke and row['Schlepph\xf6he'] == '1000':
            leistung2 = 'FSSZ' if is_student else 'FSVZ'

    result.append(leistung2)

    # VLS2PK
    result.append('T' if leistung2 else UNKNOWN_VALUE)

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

    # Einheiten - Zaehlerstand Alt
    result.append(row['M.-Start'])

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
