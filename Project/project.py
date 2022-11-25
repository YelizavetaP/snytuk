import time 
import numpy as np
import random
import sys

# import main


# population_size = 10
# n = 5           #к-сть кур'єрів піших
# m = 5            #к-сть машин
# p = 25         #к-сть пакунків
# d = [[0.0,10,5.0,3.0,8.0,4.2],
#      [10,0.0,4.0,2.0,4.7,7.0],
#      [5.0,4.0,0.0,10,5.5,2.2],
#      [3.0,2.0,10,0.0,8.9,11],
#      [8.0,4.7,5.5,8.9,0.0,1.0],
#      [4.2,7.0,2.2,11,1.1,0.0]] #матриця відстаней
# vk = 4           #швидкість кур'єра
# va = 60          #швидкість машини
# zk = 90          #зарплата кур'єра
# tsa = 15*50         #витрата пального ????
# max_weight_car = 200
# max_size_car = 2*2*1
# max_weight_human = 5
# max_size_human = 0.3*0.3*0.3



class Package(object):
    def __init__(self,address,weight,size):
        self.Address = address
        self.Weight = weight
        self.Size = size  # [length, width, hight]
        
    
    def __str__(self):
        return "Address: {}, Weight: {}, Size: {}\n".format(self.Address,self.Weight,self.Size)
    
    def detect_type(self):
        type = None
        if self.Weight>max_weight_human:
            type = "Car"
        elif len(self.Size)==3 and (self.Size[0]>=0.3 or self.Size[1]>=0.3 or self.Size[2]>=0.3):
            type = "Car"
        else:
            type = "Human"
        return type


class population(object):
    def __init__(self, population_size,packages=None,population = None):
        self.population_size = population_size
        self.packages = packages
        self.fit = None
        self.best = None
        if population==None:
            self.population = []
        else:
            self.population = population

    def fitness(self):
        sum=0.
        for i in self.population:
            sum+=i.cost
        self.fit = sum/len(self.population)

    def generate_population(self,m,n):
        if self.doPackegesFit()==False:
            print("It is imposible to destribute all packeges as we don't have enough technical or human resourses")
            sys.exit()
            
            
        self.packages = sorted(self.packages, key=lambda x:x.Weight, reverse=True)
        self.population=[]
        for _ in range(self.population_size):
            new_ind =Individ(m,n,clear=False,packages=self.packages)
            if new_ind.Delivery:
                self.population.append(new_ind)  #check if returned None
        
        self.fitness() 
        sortedPop=sorted(self.population, key=lambda x: x.cost)[:self.population_size]
        self.best = sortedPop[0]
    
    def doPackegesFit(self):
        weight=0.
        size=0.
        for pack in self.packages:
            weight+=pack.Weight
            if len(pack.Size)==3:
                size+= pack.Size[0]*pack.Size[1]*pack.Size[2]
        totalWeight = max_weight_car*m+max_weight_human*n
        totalSize = max_size_car*m
        if totalWeight<weight or totalSize<size:
            return False
        else:
            return True

    def mutate(self):
        for i in range(self.population_size):
            new =self.population[i].shuffle()
            if new !=None:
                self.population.append(new)

            new =self.population[i].exchange()
            if new !=None:
                self.population.append(new)

            new =self.population[i].returning()
            if new !=None:
                self.population.append(new)
               
        sortedPop=sorted(self.population, key=lambda x: x.cost)[:self.population_size] 
        self.find_best(sortedPop[0])
        self.update_pop(sortedPop)
              

    def find_best(self,popBest):
        if  self.best.cost> popBest.cost:
            self.best = popBest

    def update_pop(self,sortedPop):
        for i in range(self.population_size):
            self.population[i] = sortedPop[i]
        del self.population[self.population_size:]
        self.fitness()
    
    

class Individ(object):
    def __init__(self,m,n,clear,packages=None):

        self.Delivery = None
        self.cost = None
        self.generate(m,n, clear,packages)

    def __str__(self):
        text = ""
        for i in range(len(self.Delivery)):
            text+="\nRoute "+ str(i) +":\n"
            if i<m:
                text+= "Type: Car\n"
            else:
                text+= "Type Human\n"
            text+="Packages:\n"
            if self.Delivery[i]:
                for pack in self.Delivery[i]:
                    text+= str(pack)
                if i<m:
                    type="Car"
                else:
                    type="Human"
                text+= "Cost of route: {}\n".format(self.countOneRoute(self.Delivery[i],type))
                count = self.count_weight_size(self.Delivery[i])
                text+= "Weight {} out of {}, Size {}m3 out of {}m3\n".format(count[0],max_weight_car,count[1],max_size_car)
            else:
                text+="Empty\n"
        text+="Cost of delivery: {}\n".format(round(self.cost,2))
        return text
    
    def count_weight_size(self,route):
        weight =0.
        for item in route:
            weight+= item.Weight
        size =0.
        for item in route:
            if len(item.Size)==3:
                size+= item.Size[0]*item.Size[1]*item.Size[2]
        return round(weight,2),round(size,2)
        
    def find_possible_route(self,delivery,pack):
        if pack.detect_type()=="Car":
            for i, route in enumerate(delivery):
                weight, size = self.count_weight_size(route)
                weight+= pack.Weight
                size+= pack.Size[0]+pack.Size[1]+pack.Size[2]
                if weight<=max_weight_car and size <= max_size_car:
                    return i
            return None
        if pack.detect_type()=="Human":
            for i, route in enumerate(delivery):
                weight, size = self.count_weight_size(route)
                weight+= pack.Weight
                if len(pack.Size)==3:
                    size+= pack.Size[0]+pack.Size[1]+pack.Size[2]
                if weight<=max_weight_human and size <= max_size_human:
                    return i
            return None





    def generate(self,m,n,clear,packages):
        deliveries = []
        [deliveries.append([]) for _ in range(m)]
        [deliveries.append([]) for _ in range(n)]
        
        if clear==False:
            countFails = 0.
            flag=True
            for pack in packages:
                if pack.detect_type()=="Car":
                    while flag:
                        index=np.random.randint(0,m)
                        if self.check_weight("Car",route=deliveries[index],pack= pack) and self.check_size("Car",route=deliveries[index],pack= pack):
                            deliveries[index].append(pack)
                            break
                        possible_route=self.find_possible_route(deliveries[:m],pack)
                        if possible_route!=None:
                            deliveries[possible_route].append(pack)
                        else:
                            flag=False
                    if flag==False:
                        deliveries = []
                        break

                else:
                    while flag:
                        index=np.random.randint(0,n+m)
                        if index<m:
                            type="Car"
                        else:
                            type="Human"
                        fitted=self.check_size(type,route=deliveries[index],pack= pack)
                        if self.check_weight(type,route=deliveries[index],pack= pack) and fitted:
                            deliveries[index].append(pack)
                            break
                        possible_route=self.find_possible_route(deliveries,pack)
                        if possible_route!=None:
                            deliveries[possible_route].append(pack)
                        else:
                            flag=False
                    if flag==False:
                        deliveries = []
                        break

            if flag==False:
                print("Could not find the route, try to increase resourses")
                sys.exit()
            self.Delivery = deliveries
            self.count_cost()
        else:
            self.Delivery = deliveries

    


    def copy(self):
        newIndivid = Individ(m,n,clear=True)
        for i in range(len(self.Delivery)):
            newRoute=[]
            for item in self.Delivery[i]:
                newRoute.append(item)
            newIndivid.Delivery[i]= newRoute
        return newIndivid


    def count_cost(self):
        sumCar=0.
        for i,route in enumerate(self.Delivery):
            if i<m:
                type="Car"
            else:
                type = "Human"
            sumCar+= self.countOneRoute(route,type)
        self.cost = sumCar
        return

    def countOneRoute(self,route,type):
        sum=0.
        if route:
                dist=d[0][route[0].Address]
                for j in range(len(route)):
                    if j+1!= len(route):
                        dist += d[route[j].Address][route[j+1].Address]
                    else:
                        dist += d[route[j].Address][0]
                if type=="Car":
                    sum+= (dist / va) * zk + dist/100* tsa
                else:
                    sum+= (dist / vk) * zk
        return sum

    #Перемішування посилок в одному маршруті
    def shuffle(self):
        newDelivery = []
        count=0
        for i,route in enumerate(self.Delivery):
            newRoute=[]
            for j in range(len(route)):
                newRoute.append(route[j])     
            np.random.shuffle(newRoute)

            if i<m:
                type="Car"
            else:
                type="Human"

            if self.countOneRoute(newRoute,type)<self.countOneRoute(route,type):
                newDelivery.append(newRoute)
            else:
                newDelivery.append(route)
                count+=1
        if count==len(self.Delivery):
            return None
        else:
            newInd=self.copy()
            for i in range(len(newDelivery)):
                newInd.Delivery[i]= newDelivery[i]
                newInd.count_cost()
                return newInd
                  
    
    #Обмін однією посилкою між доставками однакового типу
    def exchange(self):
        indexRoute1, indexRoute2 = random.sample(range(0, m+n), 2)
        if self.Delivery[indexRoute1] and self.Delivery[indexRoute2]:
            indexItem1 = np.random.randint(0,len(self.Delivery[indexRoute1]))
            indexItem2 = np.random.randint(0,len(self.Delivery[indexRoute2]))
        else:
            return None
        
        if not (indexRoute1<m and indexRoute2<m) or not (indexRoute1>=m and indexRoute2>=m): #Packs from different types of routes
            getType1Pack = self.Delivery[indexRoute1][indexItem1].detect_type()
            getType2Pack = self.Delivery[indexRoute2][indexItem2].detect_type()
            if getType1Pack!="Human" or getType2Pack!="Human": # one pack is Car the other Human
                if np.random.random()<0.5: # generate new routes of the same category
                    indexRoute1, indexRoute2 = random.sample(range(0, m), 2)
                else:
                    indexRoute1, indexRoute2 = random.sample(range(m, m+n), 2)

                if self.Delivery[indexRoute1] and self.Delivery[indexRoute2]:
                    indexItem1 = np.random.randint(0,len(self.Delivery[indexRoute1]))
                    indexItem2 = np.random.randint(0,len(self.Delivery[indexRoute2]))
                else:
                    return None

        newRoute = self.copy()

        newRoute.Delivery[indexRoute1].append(self.Delivery[indexRoute2][indexItem2])
        newRoute.Delivery[indexRoute2].append(self.Delivery[indexRoute1][indexItem1])
        
        del newRoute.Delivery[indexRoute1][indexItem1]
        del newRoute.Delivery[indexRoute2][indexItem2]

        newRoute.count_cost()

        flag =[True,True,True,True]
        if indexRoute1<m:
            type="Car"
            
        else:
            type="Human"
        flag[0]=self.check_weight(type,newRoute.Delivery[indexRoute1])
        flag[2]=self.check_size(type,newRoute.Delivery[indexRoute1])
        if indexRoute2<m:
            type="Car"
            
        else:
            type="Human"
        flag[1]=self.check_weight(type,newRoute.Delivery[indexRoute2])
        flag[3]=self.check_size(type,newRoute.Delivery[indexRoute2])
        
        if False not in flag:
            return newRoute
        else:
            return None
    

    #видалення посилки з однієї доставки й передача в іншу

    def returning(self):
        newRoute = self.copy()
        indexRoute1, indexRoute2 = random.sample(range(0, m+n), 2)
        if self.Delivery[indexRoute1] :
            indexItem = np.random.randint(0,len(self.Delivery[indexRoute1]))
            getTypePack = self.Delivery[indexRoute1][indexItem].detect_type()
            if (getTypePack=="Car" and indexRoute2<m) or getTypePack=="Human":
                newRoute.Delivery[indexRoute2].append(self.Delivery[indexRoute1][indexItem])
                del newRoute.Delivery[indexRoute1][indexItem]
        elif self.Delivery[indexRoute2]:
                indexItem = np.random.randint(0,len(self.Delivery[indexRoute2]))
                getTypePack = self.Delivery[indexRoute2][indexItem].detect_type()
                if (getTypePack=="Car" and indexRoute1<m) or getTypePack=="Human":
                    newRoute.Delivery[indexRoute1].append(self.Delivery[indexRoute2][indexItem])
                    del newRoute.Delivery[indexRoute2][indexItem]
        else:
            return None
        

        newRoute.count_cost()

        flag =[True,True,True,True]
        if indexRoute1<m:
            type="Car"
            
        else:
            type="Human"
        flag[0]=self.check_weight(type,newRoute.Delivery[indexRoute1])
        flag[2]=self.check_size(type,newRoute.Delivery[indexRoute1])
        if indexRoute2<m:
            type="Car"
        else:
            type="Human"
        flag[1]=self.check_weight(type,newRoute.Delivery[indexRoute2])
        flag[3]=self.check_size(type,newRoute.Delivery[indexRoute2])
        
        if False not in flag:
            return newRoute
        else:
            return None
        

    def check_weight(self,type, route=None, pack=None):
        weight =0.
        for item in route:
            weight+= item.Weight
        if pack==None:
            if type=="Car":
                return weight<=max_weight_car
            else:
                return weight <=max_weight_human
        else:
            if type=="Car":
                return weight+pack.Weight<=max_weight_car
            else:
                return weight+pack.Weight <=max_weight_human

    def check_size(self,type,route,pack=None):
        size =0.
        for item in route:
            if len(item.Size)==3:
                size+= item.Size[0]*item.Size[1]*item.Size[2]
        if pack!=None:
            if len(pack.Size)==3:
                size+= pack.Size[0]*pack.Size[1]*pack.Size[2]
        if type=="Car":
            return size< max_size_car
        else:
            return size< max_size_human


            

def generate_package(packeges):
    packages=[]
    for pack in packeges:
        packages.append(Package(int(pack[0]-1),pack[1],pack[2:]))
    return packages




# class algorithm(object):
#     def __init__(self,max_iter,pop_size, n,m,packs,distance,vk,va,zk,tsa,max_weight_car=200,max_size_car=2*2*1, max_weight_human=5,max_size_human=0.3*0.3*0.3):
#         self.population = None
#         self.max_iter = max_iter
#         self.pop_size = pop_size
#         self.distances = distance
#         self.n = n
#         self.m=m
#         self.p = packs
#         self.vk = vk
#         self.va = va
#         self.zk = zk
#         self.tsa = tsa
#         self.max_weight_car = max_weight_car
#         self.max_size_car  = max_size_car
#         self.max_size_human = max_size_human
#         self.max_weight_human = max_weight_human

#     def run(self):
#         packages = generate_package(p)
#         pop = population(self.pop_size,packages = packages)
#         pop.generate_population(self.m,self.n)

#         N=0
#         while N<self.max_iter:
#             pop.mutate()
#             print("General Fit: ",pop.fit)
#             print("Best: ", pop.best.cost)
#             N+=1

#         print(pop.best)

#сюди передадуться параметри
def run(n_, m_, pCount, dCount, vk_, va_, distance, parcels, k_pay, a_pay):
    population_size = 10
    max_iter =100
    global n,m,vk,d,va,zk,  tsa, max_weight_car,max_size_car,max_weight_human,max_size_human
    n = n_           #к-сть кур'єрів піших
    m = m_            #к-сть машин
    p = parcels        #к-сть пакунків # Ліза сюди передаш дані пакунків
    d = distance #матриця відстаней
    vk = vk_           #швидкість кур'єра
    va = va_          #швидкість машини
    zk = k_pay          #зарплата кур'єра
    tsa = a_pay         #витрата пального ???? у тебе в чому вимірюється? я писала просто ціну за відстань
    max_weight_car = 200
    max_size_car = 2*2*1
    max_weight_human = 5
    max_size_human = 0.3*0.3*0.3

    packages = generate_package(p)
    pop = population(population_size,packages = packages)
    pop.generate_population(m,n)
    N=0
    while N<max_iter:
        pop.mutate()
        print("General Fit: ",pop.fit)
        print("Best: ", pop.best.cost)
        N+=1

    return pop.best



# run() #от ця функція запускатиме
