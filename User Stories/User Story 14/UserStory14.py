import redis
import pandas as pd

r = redis.Redis(db=0)
letterpoints = { "E":(1),
                 "A":(2),
                 "R":(3),
                 "I":(4),
                 "O":(5),
                 "T":(6),
                 "N":(7),
                 "S":(8),
                 "L":(9),
                 "C":(10),
                 "U":(11),
                 "D":(12),
                 "P":(13),
                 "M":(14),
                 "H":(15),
                 "G":(16),
                 "B":(17),
                 "F":(18),
                 "Y":(19),
                 "W":(20),
                 "K":(21),
                 "V":(22),
                 "X":(23),
                 "Z":(24),
                 "J":(25),
                 "Q":(26)
}
new = []
word = input("Enter your word:")
if word != []:
    z = word.split('(')[0]
    z = word.split('-')[0]
    z = word.split('–')[0]
    z = ''.join(e for e in z if e.isalnum())
    z = ''.join([i for i in z if not i.isdigit()])
    WordCount = str(len(z))
    org = z
    score = 0
    for j in z:
        j = j.upper()
        try:
            score = score + letterpoints[j]
        except KeyError:
            score = score + 0

    set = r.smembers("ANAGRAM:{}".format(score))

    listing = []
    for x in set:
        listing.append(x.decode("utf-8"))
    keys, values = zip(*(s.split(":") for s in listing))
    df = pd.DataFrame()
    df['Description'] = keys
    df['value'] = values
    key = []
    for x in df['value']:
        z = x.split('(')[0]
        z = z.split('-')[0]
        z = z.split('–')[0]
        z = ''.join(e for e in z if e.isalnum())
        z = ''.join([i for i in z if not i.isdigit()])

        if WordCount == str(len(z)):
            key.append(x +":" +str(len(z)) + ":" + z)
            new_doc = {}
            new_doc['original'] = x
            new_doc['not_original'] = z.lower()
            new_doc['match'] = x +":" +str(len(z)) + ":" + z
            new.append(new_doc)

    org = ''.join(sorted(org.lower()))
    result = []
    for kill in new:
        jugs = ''.join(sorted(kill['not_original']))
        if jugs == org:
            result.append(kill)
    # Activ Health Enhance
    key = [ sub['match'] for sub in result ]
    # print(str(key))
    Redisreturnedlist = []
    for x in key:
        Redisreturnedlist.append(x.split(":"))

    flat_list = [item for sublist in Redisreturnedlist for item in sublist]


    requiredvalues = []
    requiredvalues = flat_list[::3]
    # Function to convert
    def listToString(s):
        # initialize an empty string
        str1 = ""

        # traverse in the string
        for ele in s:
            str1 += ele

        # return string
        return str1

    listToStringval = (listToString(requiredvalues))

    if (requiredvalues == [] and listToStringval == ""):
        print("Entered word not available in our database")
    else:
        if (len(requiredvalues) > 1):
            print("Correct options available based on your search")
            print(df[df.value.isin(requiredvalues)].to_string(index=False))
        else:
            print("Correct options available based on your search")
            print(df[df.value == listToStringval].to_string(index=False))

else:
    print("Please enter non blank value ")