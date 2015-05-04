El evento a predecir, es el "resultado" de un comicio.

Dicho "resultado", es un diccionario con 
- candidatos/partidos participantes como claves, y
- la *proporcion* de los votos afirmativos obtenida como valores.

Dados los 2 millones de votos individuales involucrados en el resultados, la "suite" de hipoteticos resultados mutuamente excluyente y colectivamente exhaustivos rapidamente diverge hacia infinito punto rojo.

Es por eso que usamos la *proporcion* de votos como evento a predecir. Ademas, modificando el numero de digitos de precision de la proporcion a estimar podemos regular el tamano y "granularidad" de la suite a evaluar.

Tipicamente, usaremos dos digitos de precision, que proveen las siguientes ventajas:
- es un comodo equivalente del tradicional pero incomodo porcentaje (.17 se identifica facilmente como 17%), y
- permite que el tamano de la suite no se dispare para 4+ candidatos

===

Cada respuesta que recibimos, nos permite actualizar la distribucion del resultado ever so slightly. Para hacerlo correctamente, debemos identificar la relacion entre la respuesta obtenida, y los resultados alternativos de la suite de hipotesis.

Dada una pregunta (q: "Himmler sacara mas del 30%?"), que evidencia brindaria cada respuesta posible (r: "si"|"no")  eso a cada una de las hipotesis de la suite?

Para computar esto, debemos poder responder preguntas de la forma:

> Bajo la hipotesis "H" ({himm: 80, goeb: 20}), que probalididad hay de que un agente "A" conteste "R" ("si") a la pregunta "Q" ("Himmler sacara mas del 30%?")?



Tomemos como ejemplo una suite sencilla:
S: {
  A: {
    h: {
      himmler:  0.8
    , goebbels: 0.2
    }
    p: 0.5
  }
, B: {
    h: {
      himmler:  0.2
    , goebbels: 0.8
    }
    p: 0.5
  }
}

Suponemos que la respuesta de "A" sobre "Q"  esta determinada por un escenario mental "S" a partir del cual A "computa" sus opiniones. Si el S(A) =(h: 20, g: 80) => "R"="no"; mientras que si A piensa (h: 40, g: 60), respondera "si".

Si tomamos la decision de modelar el proceso de respuesta a traves de estos "escenarios mentales" de los agentes, la pregunta que sigue es
> como sabemos cual es el escenario mental particular que define al agente "A"?

Obviamente, no podemos saberlo con seguridad. El unico dato util que tenemos para aproximarlo, es la hipotesis bajo la cual estamos trabajando.

'a'  puede creer S=(h:5, g:95) tanto cuando H=(h:90, g:10) o H=(h: 10, g: 90): la diferencia es que esto es mucho mas comun bajo la segunda hipotesis.

Para modelar este efecto, supondremos que los escenarios mentales 's' bajo la hipotesis 'h', se pueden obtener tomando muestras aleatorias de la distribucion de votos que representa 'h'. En 'mutante.rb', el metodo 'shuffle' acepta una hipotesis, y devuelve una muestra aleatoria de si misma. Por ejemplo:

```
[14] pry(main)> 20.times { print shuffle [90,10]; print ", " }
[88, 12], [87, 13], [90, 10], [95, 5], [94, 6], [88, 12], [93, 7], [93, 7], [93, 7], [90, 10], [82, 18], [93, 7], [90, 10], [90, 10], [88, 12], [92, 8], [91, 9], [85, 15], [95, 5], [84, 16], => 20
```
