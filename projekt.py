from ctypes import Union
import sys
import time
import argparse
from typing import List, Literal, Union
from scipy.io import mmread
from petsc4py import PETSc
from pathlib import Path

def _form_str_row(*args) -> str:
    """
        Funkce, ktera formatuje dane vstupy do jedne radky tabulky.
    """
    result_str = ""
        
    for val in args:
        result_str += f"| {val:^12} "
        
    return result_str + "|"


class MatrixRecord:
    """
        Tato trida, ulozi matici jako parametr, otestuje na ni predpodminene CG a vysledky si ulozi. Zaroven je schopna vysledky vypsat.
    """
    def __init__(self, M, name: str, n_rows: int):
        self.name: str = name
        self.M = M
        self.n_rows: int = n_rows
        self.n_iters: List[Union[int, Literal['-']]] = []
        self.times: List[Union[float, Literal['-']]] = []
        
    def print_record(self, kind: Literal['n_iter', 'time']):
        """
            Funkce, ktera vypise ulozene vysledky ve formatu tabulky.
        """
        print(f"| {self.name:<12} || {f'{self.n_rows}x{self.n_rows}':^12} ", end='')
        if kind == 'n_iter':
            print(_form_str_row(*self.n_iters))
        else:
            print(_form_str_row(*self.times))
                
    def test_preconditioners(self, precons: List[str], max_iter: int=20_000, verbose: bool=False, testing_first_tim: bool = False):
        """
            Tato funkce testuje jednotlive predpodminovace.
        """
        # kazda matice potrebuje vlastni instanci ksp
        
        if verbose:
            print(f'Testing {self.name}:')
            
        ksp = PETSc.KSP().create()
        ksp.setNormType(PETSc.KSP.NormType.UNPRECONDITIONED)
        ksp.setType('cg')
        ksp.setTolerances(max_it=max_iter) # arbitrarne zvysime max pocet iteraci
        ksp_pc = ksp.getPC()
        
        # priprava prislusnych vektoru a matice k reseni
        b = self.M.createVecLeft()
        b.set(1.0)
        x = self.M.createVecRight()
        ksp.setOperators(self.M)
        
        for precon in precons:
            # nastaveni spravneho predpodminovace
            try:
                ksp_pc.setType(precon)
            except:
                if testing_first_tim:
                    print(f"Unknown preconditioner: '{precon}'.")
                self.times.append('-')
                self.n_iters.append('-')
                continue
            
            ksp.setUp()
            
            # pocatecni odhad je vzdy x = 0
            x.set(0.0)
            
            # samotne mereni
            start = time.time()
            ksp.solve(b, x)
            end = time.time()
            
            # ulozit vysledek jako ctverici ('Matice', 'size', 'pocet iteraci', 'cas (ms)')
            self.times.append(round(1000*(end - start), 3))
            self.n_iters.append(ksp.getIterationNumber())
            if verbose:
                print(f' - {precon} done.')
            
        if verbose:
            print("Done.\n")


def load_matrices() -> List[MatrixRecord]:
    """
        Funkce pro nacitani matic a pripravu "MatrixRecord" objektu.
    """
    matrices_to_test: List[MatrixRecord] = []
    
    for path in matrices_paths:
        # pipeline: .mtx -> scipy -> PETSc -> matrices_to_test
        # skript na gitu predmetu mi nefungoval -- nejaky problem s moji instalaci PETSc
        M = mmread(path).tocsr()
        A = PETSc.Mat().createAIJ(size=M.shape, csr=(M.indptr, M.indices, M.data))

        A.assemblyBegin()
        A.assemblyEnd()
        
        # extract nazev matice
        dot_index = path.rfind('.')
        slash_index = path.rfind('/')
        name = path[slash_index+1:dot_index]

        matrices_to_test.append(MatrixRecord(A, name, A.getSize()[0]))

    return matrices_to_test

def load_matrix_files(folder_path: str) -> List[str]:
    """
        Funkce pro hledani moznych matic k otestovani.
    """
    matrices_paths = []
    
    folder = Path(folder_path)
    
    for file in folder.glob(f"*{".mtx"}"):
        matrices_paths.append(str(file))

    if not matrices_paths:
        print(f"No matrices were found at '{folder_path}'!")
        sys.exit(1)
        
    return matrices_paths

# --- Main routine ---

# parsovani vstupu pro predpodpinovace, ktere chceme otestovat
parser = argparse.ArgumentParser()
parser.add_argument("-pcons", nargs="+", type=str, default=None)
parser.add_argument("-matrix_folder", type=str, default="./matrices")
parser.add_argument("--verbose", action="store_true")

args = parser.parse_args()

# nacteni zbyvajicich vstupu
if args.pcons is None:
    print("Please specify preconditioners to test!")
    sys.exit(1)

precons = args.pcons
matrix_folder_path = args.matrix_folder
verbose = args.verbose

matrices_paths = load_matrix_files(matrix_folder_path)
matrices_to_test = load_matrices()

testing_first_tim = True
for mat in matrices_to_test:
    mat.test_preconditioners(precons, verbose=verbose, testing_first_tim=testing_first_tim)
    testing_first_tim = False

# vypis vysledku
head_col = f"| {"MATRIX NAME":^12} || {"SHAPE":^12} " + _form_str_row(*precons)
head_len = len(head_col)

print(f"\n{"===  NUMER OF ITERATIONS  ===":^{head_len}}\n")
print(head_col + '\n' + head_len*"-")
for mat in matrices_to_test:
    mat.print_record(kind='n_iter')

print('\n\n')

print(f"{"===  TIME ELAPSED  ===":^{head_len}}\n")
print(head_col + '\n' + head_len*"-")
for mat in matrices_to_test:
    mat.print_record(kind='time')
    
print()