
morse_code = {
    # Alphabets
    ".-": "A", "-...": "B", "-.-.": "C",
    "-..": "D", ".": "E", "..-.": "F",
    "--.": "G", "....": "H", "..": "I",
    ".---": "J", "-.-": "K", ".-..": "L",
    "--": "M", "-.": "N", "---": "O",
    ".--.": "P", "--.-": "Q", ".-.": "R",
    "...": "S", "-": "T", "..-": "U",
    "...-": "V", ".--": "W", "-..-": "X",
    "-.--": "Y", "--..": "Z",

    # Numbers
    "-----": "0", ".----": "1",
    "..---": "2", "...--": "3",
    "....-": "4", ".....": "5",
    "-....": "6", "--...": "7",
    "---..": "8", "----.": "9",

    # Punctuation
    ".-.-.-": ".", "--..--": ",",
    "..--..": "?", ".----.": "'",
    "-.-.--": "!", "-..-.": "/",
    "-.--.": "(", "-.--.-": ")",
    ".-...": "&", "---...": ":",
    "-.-.-.": ";", "-...-": "=",
    ".-.-.": "+", "-....-": "-",
    "..--.-": "_", ".-..-.": '"',
    "...-..-": "$", ".--.-.": "@"
}


def decode_morse(code):

    words = code.strip().split(" / ")

    decoded_message = []

    for word in words:
        letters = word.split()

        decoded_word = ""

        for letter in letters:
            if letter in morse_code:
                decoded_word += morse_code[letter]
            else:
                decoded_word += "?"

        decoded_message.append(decoded_word)

    return " ".join(decoded_message)


# Test decoder independently
if __name__ == "__main__":

    code = input("Enter Morse code: ")

    result = decode_morse(code)

    print("Decoded message:", result)
