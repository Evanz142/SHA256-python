import re #regex

# ─────────CONSTANT─GENERATION────────────
constants = ["0x428a2f98", "0x71374491", "0xb5c0fbcf", "0xe9b5dba5", "0x3956c25b", "0x59f111f1", "0x923f82a4", "0xab1c5ed5", "0xd807aa98", "0x12835b01", "0x243185be", "0x550c7dc3", "0x72be5d74", "0x80deb1fe", "0x9bdc06a7", "0xc19bf174", "0xe49b69c1", "0xefbe4786", "0x0fc19dc6", "0x240ca1cc", "0x2de92c6f", "0x4a7484aa", "0x5cb0a9dc", "0x76f988da", "0x983e5152", "0xa831c66d", "0xb00327c8", "0xbf597fc7", "0xc6e00bf3", "0xd5a79147", "0x06ca6351", "0x14292967", "0x27b70a85", "0x2e1b2138", "0x4d2c6dfc", "0x53380d13", "0x650a7354", "0x766a0abb", "0x81c2c92e", "0x92722c85","0xa2bfe8a1", "0xa81a664b", "0xc24b8b70", "0xc76c51a3", "0xd192e819", "0xd6990624", "0xf40e3585", "0x106aa070","0x19a4c116", "0x1e376c08", "0x2748774c", "0x34b0bcb5", "0x391c0cb3", "0x4ed8aa4a", "0x5b9cca4f", "0x682e6ff3","0x748f82ee", "0x78a5636f", "0x84c87814", "0x8cc70208", "0x90befffa", "0xa4506ceb", "0xbef9a3f7", "0xc67178f2"]
for i in range(len(constants)):
  constants[i] = bin(int(constants[i], 16))[2:].zfill(32) 

# ────────────BASIC─OPERATIONS────────────
def shiftRight(word, n): # Shifts string to the right n times (characters shifted past the length are removed), and n zeros are added on the left
  return "0"*n+word[:-n]

def rotateRight(word, n): # String is rotated n times to the right, where the last character becomes the first character
  return word[-n:]+word[:-n]

def xor(word1, word2): # Exclusive OR operation done
  return ''.join([str(int(word1[i]) ^ int(word2[i])) for i in range(len(word1))])

def add(word1, word2): # Adds two binary numbers - converts them to decimal, adds, and the converts back. Also checks if its too long, in which case it cuts off numbers from the left side until it gets to the original input length (requires word1 and word2 to be the same length). Adds zeroes to left if the length is too short
  string = re.sub('[^0-9]','', bin(int(word1,2) + int(word2,2))) # Conversion and actual adding
  if len(string) >= len(word1):
    string = string[-1 * len(word1):] # Cutting off the extra stuff on the left (could be doing this wrong, I don't know exactly how the slicing should be done to get the string back down to 32 bits.)
    return string
  else:
    #return zeroFiller(string, "left", len(word1)-len(string)) # Adding zeroes to the left
    return string.zfill(len(word1))

# ───────────────FUNCTIONS────────────────
def lowerSigma0(word): # Lowercase Sigma 0 Function
  return xor(xor(rotateRight(word,7),rotateRight(word,18)), shiftRight(word,3))

def lowerSigma1(word): # Lowercase Sigma 1 Function
  return xor(xor(rotateRight(word,17),rotateRight(word,19)), shiftRight(word,10))

def upperSigma0(word): # Uppercase Sigma 0 Function
  return xor(xor(rotateRight(word,2),rotateRight(word,13)), rotateRight(word,22))

def upperSigma1(word): # Uppercase Sigma 1 Function
  return xor(xor(rotateRight(word,6),rotateRight(word,11)), rotateRight(word,25))

def choice(wordX, wordY, wordZ): # Choice function
  return ''.join([(wordY[i] if wordX[i]=="1" else wordZ[i]) for i in range(len(wordX))])

def majority(wordX, wordY, wordZ): # Majority function
  return ''.join([("1" if int(wordX[i])+int(wordY[i])+int(wordZ[i])>=2 else "0")for i in range(len(wordX))])

# ───────────────PADDING────────────────
def addPadding(binaryString):
  binaryString += "1"
  binaryStringLength = len(binaryString)
  messageBlockMultiplier = (binaryStringLength // 512) + 1
  if binaryStringLength >= (messageBlockMultiplier * 512) - 64: # To check if it ends inside the space set aside to write the length, and if so, then it needs to pad up to the next multiple of 512
    messageBlockMultiplier += 1
  binaryOriginalLength = re.sub('[^0-9]','', bin(binaryStringLength - 1)) # Binary for the length of the original input  
  for i in range((messageBlockMultiplier * 512) - binaryStringLength - len(binaryOriginalLength)): # Adds zeroes for padding up to the start of the length space, and also adds zeros inside the length space until it reaches the spot where the actual binary of the length needs to start
    binaryString += "0"
    i += 1
  binaryString += binaryOriginalLength
  return [binaryString, messageBlockMultiplier]

# ───────────────MESSAGE─SCHEDULE───────────────
def createMessageSchedule(binaryString):
# Message schedule calculations
  messageSchedule = [binaryString[i:i+32] for i in range(0, len(binaryString), 32)] # Splits the binary string into a list of words (chunks of 32 bit binary sequences)
  while len(messageSchedule) < 64: # Adds to message schedule until there are 64 words
    length = len(messageSchedule)

    # The following is the formula to create new words via using functions on previous words and then adding them.
    string = add(lowerSigma1(messageSchedule[length-2]),messageSchedule[length-7])
    string = add(string,lowerSigma0(messageSchedule[length-15]))
    string = add(string,messageSchedule[length-16])
    messageSchedule.append(string) # Add the new word to the message schedule  
  return messageSchedule

# ───────────────COMPRESSION───────────────
'''
Letter values to indices
a = 0
b = 1
c = 2
d = 3
e = 4
f = 5
g = 6
h = 7
'''
def compression(hashValues, messageSchedule):
  for i in range(len(messageSchedule)):

    # Creating the first temporary word
    # ─────────────────────────────────
    t1 = upperSigma1(hashValues[4]) # Upper Sigma 1 function of index 4 in the current hash values
    t1 = add(t1, choice(hashValues[4],hashValues[5],hashValues[6])) # Add to choice( indices 4, 5, and 6 ) in the current hash values
    t1 = add(t1, hashValues[7]) # Add to index 7 in the current hash values
    t1 = add(t1, constants[i]) # Add to index i in the list of constants
    t1 = add(t1, messageSchedule[i]) # Add to index i in the message schedule (word i)

    # Creating the second temporary word
    # ──────────────────────────────────
    t2 = upperSigma0(hashValues[0]) # Upper Sigma 0 function of index 0 in the current hash values
    t2 = add(t2, majority(hashValues[0],hashValues[1],hashValues[2])) # Add to majority( indices 0, 1, and 2 ) in the current hash values

    # Compress the hash values
    # ────────────────────────
    hashValues = [add(t1,t2)] + hashValues[:-1] # Shift the list down one (last element is removed), and insert t1 + t2 as the new first element
    hashValues[4] = add(hashValues[4], t1) # Add t1 to index 4 in the hash values
  
  return hashValues


# Original input
string = input("Enter Message: ")
print("Length: "+str(len(string))+"\n──────────────\n")

# Converting original input into ASCII
asciiValues = []
for char in string:
  asciiValues.append(ord(char))
print("Ascii Values: ", end='');print(asciiValues)

# Converting ASCII into binary
binaryString = ''
for i in asciiValues:
  binaryString += bin(i)
binaryString = re.sub('[^0-9]','', binaryString) # The bin() function automatically adds the letter 'b' into the converted number, so this line removes all alphanumeric characters.
print("Binary String: " + binaryString)

print("\n──────────────\n")
# Adding padding to the binary string
binaryString,messageBlockMultiplier = addPadding(binaryString)
print("Padded Binary String: " + binaryString + "\nMessage Blocks: " + str(messageBlockMultiplier))

# Initial Hash Values
a = "01101010000010011110011001100111"
b = "10111011011001111010111010000101"
c = "00111100011011101111001101110010"
d = "10100101010011111111010100111010"
e = "01010001000011100101001001111111"
f = "10011011000001010110100010001100"
g = "00011111100000111101100110101011"
h = "01011011111000001100110100011001"
initialHashValues = [a,b,c,d,e,f,g,h]
hashValues = [a,b,c,d,e,f,g,h]

messageBlocks = [binaryString[i:i+512] for i in range(0, len(binaryString), 512)] # Splits up padded message into a list of message blocks (Each being 512 bits)

for i in messageBlocks:
  messageSchedule = createMessageSchedule(i) # Creates the message schedule for each seperate message block
  hashValues = compression(hashValues, messageSchedule) # Calculates the hash values for each message schedule, and uses updated hash values in case of multiple message blocks

for i in range(len(hashValues)):
  hashValues[i] = add(hashValues[i], initialHashValues[i]) # Add the initial hash values (constants) to back to the current changed hash values

print("\n──────────────\n")
# Creates the message schedule 

print("Final Binary Hash Values: \n") # Prints the final binary hash values
for i in hashValues:
  print(i)

print("\n──────────────\n")

finalHash = ''
for i in hashValues: # Converts all the final hash values into hexadecimal and then concatenates them into one string
  finalHash += hex(int(i, 2))[2:]

print("Final Hash Value: \n" + finalHash) # Prints the final hash

#zyxwvutsrqponmlkjihdfedcabzabcdefghijklmnopqrtwuvxyzzyxwvutsrqponlkjihgfedcababcdefghijklmnopqrstuwvyxzzyxwvutsrqpnlkjihdfedcab
