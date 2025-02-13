import datetime

def is_vowel(char):

    return char.lower() in "aeiou"
 
def cf_name(name):

    name = "".join(filter(str.isalpha, name))

    if len(name) < 3:

        return name.upper() + "X"

    consonants = "".join([c for c in name if not is_vowel(c)]).upper()

    vowels = "".join([c for c in name if is_vowel(c)]).upper()

    if len(consonants) < 4:

        if len(consonants) < 3:

            return (consonants + vowels[:2]).upper()[:3]

        return consonants.upper()

    return (consonants[0] + consonants[2] + consonants[3]).upper()
 
def cf_surname(surname):

    surname = "".join(filter(str.isalpha, surname))

    if len(surname) < 3:

        return surname.upper() + "X"

    consonants = "".join([c for c in surname if not is_vowel(c)]).upper()

    vowels = "".join([c for c in surname if is_vowel(c)]).upper()

    if len(consonants) < 3:

        return (consonants + vowels[:2]).upper()[:3]

    return (consonants[:3]).upper()
 

def codice_data_nascita(data_nascita, sesso):
    mese_codice = 'ABCDEHLMPRST'
    data = datetime.datetime.strptime(data_nascita, '%Y-%m-%d')
    anno = str(data.year)[-2:]
    mese = mese_codice[data.month - 1]
    giorno = data.day + 40 if sesso == 'F' else data.day
    giorno = f'{giorno:02d}'
    return anno + mese + giorno

comuni = {
    'ROMA': 'H501',
    'MILANO': 'F205',
    'NAPOLI': 'F839',
    # Aggiungi altri comuni qui
}

def codice_comune(comune):
    return comuni.get(comune.upper(), 'XXXX')



def cf_special(half_cf):
    odd_values = {
        'A': 1, 'B': 0, 'C': 5, 'D': 7, 'E': 9, 'F': 13, 'G': 15, 'H': 17, 'I': 19, 'J': 21,
        'K': 2, 'L': 4, 'M': 18, 'N': 20, 'O': 11, 'P': 3, 'Q': 6, 'R': 8, 'S': 12, 'T': 14,
        'U': 16, 'V': 10, 'W': 22, 'X': 25, 'Y': 24, 'Z': 23,
        '0': 1, '1': 0, '2': 5, '3': 7, '4': 9, '5': 13, '6': 15, '7': 17, '8': 19, '9': 21
    }
    even_values = {
        'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7, 'I': 8, 'J': 9,
        'K': 10, 'L': 11, 'M': 12, 'N': 13, 'O': 14, 'P': 15, 'Q': 16, 'R': 17, 'S': 18, 'T': 19,
        'U': 20, 'V': 21, 'W': 22, 'X': 23, 'Y': 24, 'Z': 25,
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
    }
    somma = sum(odd_values[half_cf[i]] for i in range(0, len(half_cf), 2))
    somma += sum(even_values[half_cf[i]] for i in range(1, len(half_cf), 2))
    return chr(somma % 26 + ord('A'))

def genera_codice_fiscale(nome, cognome, data_nascita, sesso, comune):
    cf = cf_surname(cognome)
    cf += cf_name(nome)
    cf += codice_data_nascita(data_nascita, sesso)
    cf += comune
    cf += cf_special(cf)
    return cf

def main():
    print("Generatore di Codice Fiscale")

    cognome = input("Inserisci il cognome: ")
    nome = input("Inserisci il nome: ")
    data_nascita = input("Inserisci la data di nascita (dd/mm/yyyy): ")
    sesso = input("Inserisci il sesso (M/F): ").upper()
    comune = input("Inserisci il comune di nascita: ")

    codice_fiscale = genera_codice_fiscale(nome, cognome, data_nascita, sesso, comune)
    print(f"Il tuo codice fiscale è: {codice_fiscale}")
