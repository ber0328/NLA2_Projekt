# NLA2_Projekt
Repozitář s projektem do předmětu NLA2.

Program je psaný v pythonu, takze neni co kompilovat.
Předpodmiňovače k otestování se očekávají jako vstupní argument s vlaječkou "-pcons".
Program lze spustit v libovolném prostředí obsahující petsc4py a scipy příkazem:

```bash
python3 projekt.py -pcons jacobi sor ilu icc none
```

Pro výpis informací o tom co již bylo testováno, lze použít vlaječku
```bash
--verbose
```
