import copy

# fct. de inversare literal
# (ex: x -> -x și -x -> x)
def inverseazaLiteral(literal):
    return str(-int(literal))

# fct. de gasire a perechilor de clauze rezolvabile
def gasirePerecheRezolvabila(clauze):
    for clA in range(len(clauze) - 1):
        for clB in range(clA + 1, len(clauze)):
            r = rezolvaClauze(clauze[clA], clauze[clB])
            # daca s-a rezolvat ceva nou ...
            if (r is not None and r not in clauze): 
                # ... adauga în lista de clauze
                return r
    return None

# fct. de rezolvare a clauzelor
# (ex: {x, y}, {-x, z} -> {y, z})
def rezolvaClauze(clauzaA, clauzaB):
    for lit in clauzaA:
        litInversat = inverseazaLiteral(lit)
        if (litInversat in clauzaB):
            clauzaNoua = set(clauzaA.union(clauzaB))
            clauzaNoua.discard(lit)
            clauzaNoua.discard(litInversat)
            return clauzaNoua
    return None

# algoritmul de Rezolutie
def algoRezolutie(clauze):
    clInitiale = copy.deepcopy(clauze)
    clRezolvabila = gasirePerecheRezolvabila(clInitiale)
    while (clRezolvabila is not None):
        if (len(clRezolvabila) == 0):
            # nesatisfiabil
            return False
        clInitiale.append(clRezolvabila)
        clRezolvabila = gasirePerecheRezolvabila(clInitiale)
    # satisfiabil
    return True

# fct. de propagare unitara
# (ex: {{-x, y}, {x, -z}, {y, z}}, x -> {{y}, {y, z}})
def propagareUnitara(clauze, targetLit):
    clauzeActualizate = []
    litInversat = inverseazaLiteral(targetLit)
    for clauza in clauze:
        if (targetLit in clauza):
            continue
        if (litInversat in clauza):
            clauzaNoua = clauza - {litInversat}
            clauzeActualizate.append(clauzaNoua)
        else:
            clauzeActualizate.append(clauza)
    return clauzeActualizate

# fct. de cautare clauza cu un singur literal
# (ex: {{x, y}, {y}, {-x, z}} -> {y})
def gasesteClauzaUnitara(clauze):
    for clauza in clauze:
        if (len(clauza) == 1):
            return next(iter(clauza))
    return None

# fct. de cautare literal pur
# (ex: {{x, y}, {y, -z}, {-x, z}} -> {y})
def gasesteLiteralPur(clauze):
    toateLiteralele = set().union(*clauze)
    for lit in toateLiteralele:
        if (inverseazaLiteral(lit) not in toateLiteralele):
            return lit
    return None

# fct. de eliminarea tuturor clauzelor care contin un literal pur
def regulaLiteralPur(clauze, targetLit):
    return [clauza for clauza in clauze if (targetLit not in clauza)]

# algoritmul Davis-Putnam (DP)
def algoDP(clauze):
    clInitiale = copy.deepcopy(clauze)
    while (len(clInitiale) > 0):
        if (any(len(clauza) == 0 for clauza in clInitiale)):
            return False

        litUnitar = gasesteClauzaUnitara(clInitiale)
        if (litUnitar is not None):
            clInitiale = propagareUnitara(clInitiale, litUnitar)
            continue

        litPur = gasesteLiteralPur(clInitiale)
        if (litPur is not None):
            clInitiale = regulaLiteralPur(clInitiale, litPur)
            continue

        return algoRezolutie(clInitiale)
    return True

# algoritmul DPLL (Davis-Putnam-Logemann-Loveland)
def algoDPLL(clauze):
    clInitiale = copy.deepcopy(clauze)
    while (len(clInitiale) > 0):
        if (any(len(clauza) == 0 for clauza in clInitiale)):
            return False

        litUnitar = gasesteClauzaUnitara(clInitiale)
        if (litUnitar is not None):
            clInitiale = propagareUnitara(clInitiale, litUnitar)
            continue

        litPur = gasesteLiteralPur(clInitiale)
        if (litPur is not None):
            clInitiale = regulaLiteralPur(clInitiale, litPur)
            continue

        litAles = next(iter(clInitiale[0]))
        ramuraPozitiva = propagareUnitara(copy.deepcopy(clInitiale), litAles)
        if (algoDPLL(ramuraPozitiva)):
            return True
        ramuraNegativa = propagareUnitara(copy.deepcopy(clInitiale), inverseazaLiteral(litAles))
        return algoDPLL(ramuraNegativa)

    return True

def citireDimacs(path):
    clauze = []
    nrClauzeDeclarate = None
    try:
        with open(path, 'r') as f:
            for linie in f:
                linie = linie.strip()
                if linie.startswith('c') or linie == '':
                    continue
                if linie.startswith('p'):
                    parts = linie.split()
                    if len(parts) >= 4 and parts[1] == 'cnf':
                        try:
                            nrClauzeDeclarate = int(parts[3])
                        except:
                            return None, "Eroare clauze"
                    continue
                litere = linie.split()
                if litere[-1] == '0':
                    litere.pop()
                clauze.append(set(litere))
    except:
        return None, "Eroare deschidere fișier"

    if nrClauzeDeclarate is not None and len(clauze) != nrClauzeDeclarate:
        return None, "Eroare clauze"

    return clauze, None

def run(inputFile):
    print("Script de testare a algoritmilor de satisfiabilitate")
    print("Algoritmi: Rezolutie, Davis-Putnam, DPLL")

    print(f"Se analizează fișierul {inputFile}...\n")
    clauze, eroare = citireDimacs(inputFile)

    if eroare:
        print(eroare)
        return

    print("Rezolutie:", "Satisfiabil" if algoRezolutie(clauze) else "Nesatisfiabil")

    print("Davis-Putnam:", "Satisfiabil" if algoDP(clauze) else "Nesatisfiabil")

    print("DPLL:", "Satisfiabil" if algoDPLL(clauze) else "Nesatisfiabil")
    
    print("Cod finalizat!")
    print("--------------------------------------------------")

run('teste/formula_medie.cnf')
