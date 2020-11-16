import random as rnd
class Trivia:
    def __init__ (self):
        # Lista de IDs das questões que foram selecionadas através do método "taken by one"
        self.__taken_by_one = []

        self.__questions = [
            (1,"What's the name of the protagonist of The Legend of Zelda's Series?","Link"),
            (2,"Who's the father of Luke Skywalker?","Anakin Skywalker"),
            (3,"What's the name of the creator of Doki Doki Literature Club?","Dan Salvato"),
            (4,"What's the name of the main character of the Manga Berserk?","Guts"),
            (5,"What's the name of the time Machine of the Doctor on the TV show Doctor Who?","TARDIS"),
            (6,"In which Language this program was made?","Python"),
        ]

    def get_one (self):
        out_loop = False
        while not out_loop:
            random_question = rnd.randint(1,len(self.__questions))
            if random_question not in self.__taken_by_one:
                self.__taken_by_one.append(random_question) 
                out_loop = True

                if len(self.__taken_by_one) == len(self.__questions):#then
                    self.__taken_by_one = []
        return self.__questions[random_question-1][1:]

if __name__ == "__main__":
    test = Trivia()
    ha = []
    for i in range(6):
        ha.append(test.get_one())

    for i in ha:
        print(i)