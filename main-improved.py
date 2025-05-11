from copy import deepcopy
from collections import Counter

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
    # salvam clauzele initiale intr-un format set pe care il putem modifica
    clauze = list(map(frozenset, deepcopy(clauze)))
    clauzeCunoscute = set(clauze)

    # creem un set unde vom adauga perechile de clauze verificate
    # pentru a evita verificarea lor de mai multe ori
    # (ex: {x, y}, {-x, z} -> {y, z} este aceeasi cu {-x, z}, {x, y} -> {y, z})
    perechiVerificate = set()

    listaClauze = list(clauzeCunoscute)
    for i in range(len(listaClauze)):
        for j in range(i + 1, len(listaClauze)):
            c1, c2 = listaClauze[i], listaClauze[j]
            # verificam daca am mai verificat perechea ...
            if (c1, c2) in perechiVerificate or (c2, c1) in perechiVerificate:
                continue
            # ... daca nu, o adaugam in setul de perechi verificate
            perechiVerificate.add((c1, c2))
            for lit in c1:
                if inverseazaLiteral(lit) in c2:
                    litOpus = inverseazaLiteral(lit)
                    rezolvent = set(c1.union(c2))
                    rezolvent.discard(lit)
                    rezolvent.discard(litOpus)
                    # verificam daca rezolventul este gol
                    if not rezolvent:
                        # => nesatisfiabil
                        return False
                    # verificam daca rezolventul este nou
                    if frozenset(rezolvent) not in clauzeCunoscute:
                        clauzeCunoscute.add(frozenset(rezolvent))
                        listaClauze.append(frozenset(rezolvent))
    # => satisfiabil
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
    cl = list(map(set, clauze))
    totiLiteralii = set().union(*cl)
    for lit in totiLiteralii:
        if inverseazaLiteral(lit) not in totiLiteralii:
            cl = [c for c in cl if lit not in c]
            totiLiteralii = set().union(*cl)
            break

    # se aplica iterativ propagarea literalelor unice și eliminarea celor puri
    schimbat = True
    while schimbat:
        schimbat = False

        # verificare clauza goala
        if any(len(c) == 0 for c in cl):
            return False

        # propagare literal unitar (clauze cu un singur literal)
        unitari = [next(iter(c)) for c in cl if len(c) == 1]
        if unitari:
            schimbat = True
            for lit in unitari:
                litOpus = inverseazaLiteral(lit)
                cl = [c - {litOpus} if litOpus in c else c for c in cl if lit not in c]

        # eliminare literal pur (care apare doar pozitiv sau doar negativ)
        totiLiteralii = set().union(*cl)
        for lit in totiLiteralii:
            if inverseazaLiteral(lit) not in totiLiteralii:
                cl = [c for c in cl if lit not in c]
                schimbat = True
                break

    return algoRezolutie(cl)

# algoritmul DPLL (Davis-Putnam-Logemann-Loveland)
def algoDPLL(clauze, variantaAlegereLiteral):
    cl = list(map(set, clauze))
    # verifica clauza goala (contradictie)
    if any(len(c) == 0 for c in cl):
        return False
    # daca nu mai sunt clauze, formula e satisfiabila
    if not cl:
        return True

    # propagare literal unitar
    for c in cl:
        if len(c) == 1:
            lit = next(iter(c))
            litOpus = inverseazaLiteral(lit)
            cl_nou = [ci - {litOpus} if litOpus in ci else ci for ci in cl if lit not in ci]
            return algoDPLL(cl_nou, variantaAlegereLiteral)

    # eliminare literal pur (care apare doar pozitiv sau doar negativ)
    totiLiteralii = set().union(*cl)
    for lit in totiLiteralii:
        if inverseazaLiteral(lit) not in totiLiteralii:
            cl_nou = [ci for ci in cl if lit not in ci]
            return algoDPLL(cl_nou, variantaAlegereLiteral)

    if variantaAlegereLiteral == 1:
        # alegere literal oarecare
        lit = next(iter(cl[0]))
    elif variantaAlegereLiteral == 2:
        # alegere literal dupa frecventa
        counter = Counter()
        for ci in cl:
            for lit in ci:
                counter[lit] += 1
        lit = counter.most_common(1)[0][0]  # literalul cel mai frecvent

    litOpus = inverseazaLiteral(lit)

    clAdev = [ci - {litOpus} if litOpus in ci else ci for ci in cl if lit not in ci]
    if algoDPLL(clAdev, variantaAlegereLiteral):
        return True

    clFalse = [ci - {lit} if lit in ci else ci for ci in cl if litOpus not in ci]
    return algoDPLL(clFalse, variantaAlegereLiteral)

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
    
    print("Rezolutie:", "Satisfiabil" if algoRezolutie(deepcopy(clauze)) else "Nesatisfiabil")

    print("Davis-Putnam:", "Satisfiabil" if algoDP(deepcopy(clauze)) else "Nesatisfiabil")

    print("DPLL 1:", "Satisfiabil" if algoDPLL(deepcopy(clauze), 1) else "Nesatisfiabil")
    print("DPLL 2:", "Satisfiabil" if algoDPLL(deepcopy(clauze), 2) else "Nesatisfiabil")
    
    print("Cod finalizat!")
    print("--------------------------------------------------")

run('teste/formula_mare.cnf')
