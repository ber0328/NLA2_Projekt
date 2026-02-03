# NLA2_Projekt
Repozitář s projektem do předmětu NLA2.

Program je psaný v pythonu, takze neni co kompilovat. Používáme knihovnu petsc4py.

Předpodmiňovače k otestování se očekávají jako vstupní argument s vlaječkou "-pcons".

Předpodmiňovač se očekává pod stejným názvem jako v PETSc. 'none' označuje situaci, kdy není použit předpodmiňovač.

Program lze spustit například takto:
```bash
python3 projekt.py -pcons jacobi sor ilu icc none
```

Pro výpis informací o tom co již bylo testováno, lze použít vlaječku '--verbose':
```bash
python3 projekt.py -pcons none --verbose
```

Slozku s maticemi k otestovani lze specifikovat vlaječkou '-matrix_folder':
```bash
python3 projekt.py -matrix_folder [moje_skvela_slozka] -pcons sor gamg
```

Pokud vlaječku nepoužijeme, program bude matice hledat ve složce './matrices'. Matice se očekávájí ve formátu '.mtx'.
