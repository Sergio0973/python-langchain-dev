# Resultados del taller RAG Nestlé

## Pregunta

capital de tunez?

## Escenario base

- `chunk_size`: 1000
- `chunk_overlap`: 200
- `k`: 4
- `temperature`: 0.1
- Chunks generados: 35

### Respuesta

Respuesta general (no proviene del documento):  
La capital de Túnez es Túnez.

### Fragmentos recuperados

#### Fragmento 1 — página 8

ANEXO A 
 
TIENDAS 
 
1. C&C Queretaro: Plaza Zimapán #234 Plazas del Sol 3ra Sección, Delegación Josefa 
Vergara y Hernandez C.P. 76099, Queretaro, Queretaro. 
 
2. C&C Celaya: Av., Constituyentes Esq.  Con Antonio Plaza #419 Centro, C.P. 38090, 
Celaya Gto. 
 
3. C&C Cortazar: Fco. I Madero #109, Centro, C.P. 38300, Cortazar, Gto. 
 
4. Autoservicio Jaral: José María Morelos #228, Centro, C.P. 38470, Jaral del Progreso, Gto

#### Fragmento 2 — página 5

responsabilidad por cualquier falla técnica o un funcionamiento defectuoso o cualquier otro 
problema con la red que es té conectado en línea al sistema, servidores, o proveedores de 
otro tipo, que puede ser el resultado de cualquier contenido o entrada en la promoción que 
no esté correctamente registrado. Todas las cuestiones y controversias serán sometidas a 
la decisión final del mismo. 
- La Organizadora no se hace cargo de los gastos que generen, suministro de energía 
eléctrica, servicio de telecomunicaciones, programas y software y hardware, reproductores 
musicales, ni recomienda o promueve marca alguna de insumos tecnológicos y cualquier 
otro requisito de participación. 
- Todos los participantes que  acepten las bases, términos y condiciones de la promoción, 
aceptan en forma adicional, que los mismos puedan ser modificados por los organizadores 
así como de las decisiones que adopten sobre cualquier cuestión prevista o no prevista en

#### Fragmento 3 — página 1

BASES Y MECÁNICAS DE LA PROMOCIÓN 
 
“SU PARTICIPACIÓN EN LA PRESENTE PROMOCIÓN COMERCIAL, CONSTITUYE SU 
ADHESIÓN Y ACEPTACIÓN SIN RESERVA ALGUNA DE LOS PRESENTES TÉRMINOS, 
CONDICIONES, RESTRICCIONES Y AVISO DE PRIVACIDAD, POR LO QUE LE 
RECOMENDAMOS QUE ANTES DE PARTICIPAR LAS LEA CUIDADOSAMENTE A FIN DE QUE 
LAS ANALICE Y CONCIENTEMENTE PARTICIPE O SE ABSTENGA DE ELLO. 
 
Nombre de la promoción: “Ofertas de Hoy con Inés Básicos” 
 
Responsable y organizadora de la promoción: Desarrollo Comercial Abarrotero SA de CV. Con 
domicilio carr. cortazar-estacion km 1.5 s/n predio Santa Anita c.p 38300 Cortazar, Gto 
 
 
Cobertura Geográfica: Nacional, a través de todas las tiendas Básicos (ver anexo A para identificar 
las tiendas). 
 
Vigencia: Del 01 de febrero al 15 de marzo de 2019. 
 
Tiendas participantes: Las tiendas Basicos  de la República Mexicana  que emitan un ticket de 
compra formal siempre y cuando contenga los siguientes elementos: 
 
• Número de ticket

#### Fragmento 4 — página 5

- Si por cualquier razón, la promoción no es capaz de ejecutarse tal y com o estaba previsto, 
incluyendo, alguna limitación, la infección por virus de computadora, bugs, la manipulación, 
intervención no autorizada, el fraude, fallas técnicas o cualquier otra causa corrupta o que 
afecte a la administración, seguridad, equidad, int egridad o la correcta realización de la 
promoción, Desarrollo Comercial Abarrotero ., sus subsidiarias y/o afiliadas se reservan el 
derecho, a su sola discreción para cancelar, demorar, modificar o terminar la promoción; 
previo aviso al público y siempre y cuando no afecte los derechos de los participantes. 
- Desarrollo Comercial Abarrotero., y sus subsidiarias y/o afiliadas no aceptan ninguna 
responsabilidad por cualquier falla técnica o un funcionamiento defectuoso o cualquier otro 
problema con la red que es té conectado en línea al sistema, servidores, o proveedores de

## Escenario 1: chunks pequeños y menos fragmentos

- `chunk_size`: 350
- `chunk_overlap`: 20
- `k`: 2
- `temperature`: 0.1
- Chunks generados: 90

### Respuesta

Respuesta general (no proviene del documento):  
La capital de Túnez es Túnez.

### Fragmentos recuperados

#### Fragmento 1 — página 8

ANEXO A 
 
TIENDAS 
 
1. C&C Queretaro: Plaza Zimapán #234 Plazas del Sol 3ra Sección, Delegación Josefa 
Vergara y Hernandez C.P. 76099, Queretaro, Queretaro. 
 
2. C&C Celaya: Av., Constituyentes Esq.  Con Antonio Plaza #419 Centro, C.P. 38090, 
Celaya Gto. 
 
3. C&C Cortazar: Fco. I Madero #109, Centro, C.P. 38300, Cortazar, Gto.

#### Fragmento 2 — página 1

M.N. (setenta pesos 00/100 moneda nacional) en productos participantes de la marca Nestlé, podrá 
participar en la promoción para intentar ganarse uno de los premios mencionados anteriormente.

## Escenario 2: más fragmentos recuperados

- `chunk_size`: 1000
- `chunk_overlap`: 200
- `k`: 6
- `temperature`: 0.1
- Chunks generados: 35

### Respuesta

Respuesta general (no proviene del documento):  
La capital de Túnez es Túnez. Es la ciudad más grande y la capital del país Túnez, ubicado en el norte de África.

### Fragmentos recuperados

#### Fragmento 1 — página 8

ANEXO A 
 
TIENDAS 
 
1. C&C Queretaro: Plaza Zimapán #234 Plazas del Sol 3ra Sección, Delegación Josefa 
Vergara y Hernandez C.P. 76099, Queretaro, Queretaro. 
 
2. C&C Celaya: Av., Constituyentes Esq.  Con Antonio Plaza #419 Centro, C.P. 38090, 
Celaya Gto. 
 
3. C&C Cortazar: Fco. I Madero #109, Centro, C.P. 38300, Cortazar, Gto. 
 
4. Autoservicio Jaral: José María Morelos #228, Centro, C.P. 38470, Jaral del Progreso, Gto

#### Fragmento 2 — página 5

responsabilidad por cualquier falla técnica o un funcionamiento defectuoso o cualquier otro 
problema con la red que es té conectado en línea al sistema, servidores, o proveedores de 
otro tipo, que puede ser el resultado de cualquier contenido o entrada en la promoción que 
no esté correctamente registrado. Todas las cuestiones y controversias serán sometidas a 
la decisión final del mismo. 
- La Organizadora no se hace cargo de los gastos que generen, suministro de energía 
eléctrica, servicio de telecomunicaciones, programas y software y hardware, reproductores 
musicales, ni recomienda o promueve marca alguna de insumos tecnológicos y cualquier 
otro requisito de participación. 
- Todos los participantes que  acepten las bases, términos y condiciones de la promoción, 
aceptan en forma adicional, que los mismos puedan ser modificados por los organizadores 
así como de las decisiones que adopten sobre cualquier cuestión prevista o no prevista en

#### Fragmento 3 — página 1

BASES Y MECÁNICAS DE LA PROMOCIÓN 
 
“SU PARTICIPACIÓN EN LA PRESENTE PROMOCIÓN COMERCIAL, CONSTITUYE SU 
ADHESIÓN Y ACEPTACIÓN SIN RESERVA ALGUNA DE LOS PRESENTES TÉRMINOS, 
CONDICIONES, RESTRICCIONES Y AVISO DE PRIVACIDAD, POR LO QUE LE 
RECOMENDAMOS QUE ANTES DE PARTICIPAR LAS LEA CUIDADOSAMENTE A FIN DE QUE 
LAS ANALICE Y CONCIENTEMENTE PARTICIPE O SE ABSTENGA DE ELLO. 
 
Nombre de la promoción: “Ofertas de Hoy con Inés Básicos” 
 
Responsable y organizadora de la promoción: Desarrollo Comercial Abarrotero SA de CV. Con 
domicilio carr. cortazar-estacion km 1.5 s/n predio Santa Anita c.p 38300 Cortazar, Gto 
 
 
Cobertura Geográfica: Nacional, a través de todas las tiendas Básicos (ver anexo A para identificar 
las tiendas). 
 
Vigencia: Del 01 de febrero al 15 de marzo de 2019. 
 
Tiendas participantes: Las tiendas Basicos  de la República Mexicana  que emitan un ticket de 
compra formal siempre y cuando contenga los siguientes elementos: 
 
• Número de ticket

#### Fragmento 4 — página 5

- Si por cualquier razón, la promoción no es capaz de ejecutarse tal y com o estaba previsto, 
incluyendo, alguna limitación, la infección por virus de computadora, bugs, la manipulación, 
intervención no autorizada, el fraude, fallas técnicas o cualquier otra causa corrupta o que 
afecte a la administración, seguridad, equidad, int egridad o la correcta realización de la 
promoción, Desarrollo Comercial Abarrotero ., sus subsidiarias y/o afiliadas se reservan el 
derecho, a su sola discreción para cancelar, demorar, modificar o terminar la promoción; 
previo aviso al público y siempre y cuando no afecte los derechos de los participantes. 
- Desarrollo Comercial Abarrotero., y sus subsidiarias y/o afiliadas no aceptan ninguna 
responsabilidad por cualquier falla técnica o un funcionamiento defectuoso o cualquier otro 
problema con la red que es té conectado en línea al sistema, servidores, o proveedores de

#### Fragmento 5 — página 6

AVISO DE PRIVACIDAD 
1. Identidad y Domicilio del Responsable de sus Datos Personales.  
 
Desarrollo Comercial Abarrotero SA de CV  en lo sucesivo “DECASA” con domicilio en CARR. CORTAZAR -ESTACION 
KM 1.5 S/N PREDIO SANTA ANITA C.P 38300 CORTAZAR, GTO, será responsable del uso, tratamiento y protección de sus 
datos personales en términos de la Ley Federal de Protección de Datos Personales en Posesión de los Particulares.  
Así mismo, le informamos que de ninguna manera manejamos datos sensibles; por tal razón, deberá abstenerse de 
proporcionar datos de esa índole.  
 
2. Datos personales recabados.  
En virtud de su participación en la promoción desplegada, en lo sucesivo “la promoción”, de la cual es responsable DECASA 
con domicilio en CARR. CORTAZAR-ESTACION KM 1.5 S/N PREDIO SANTA ANITA C.P 38300 CORTAZAR, GTO 
 
a) Para participar en la Promoción, Usted deberá proporcionar la siguiente información personal, en términos de las Bases de 
la Promoción:

#### Fragmento 6 — página 6

a) Para participar en la Promoción, Usted deberá proporcionar la siguiente información personal, en términos de las Bases de 
la Promoción:  
 
- Nombre completo (nombre(s), apellido paterno y apellido materno)  
- Correo electrónico  
- Teléfonos de contacto (casa/móvil)  
- Ticket de compra  
- Estado  
 
b) En caso de resultar ganador de la Promoción, confo rme las Bases, deberá presentar y entregar físicamente la siguiente 
documentación:  
 
- Copia de identificación oficial vigente con fotografía por ambos lados.  
- Domicilio completo 
 
Los datos personales anteriores y todos aquellos que se pudieran desprender de la entrega de los documentos anteriormente 
descritos, serán denominados en conjunto y en lo sucesivo “datos personales”. Asimismo, NO recabamos datos personales 
sensibles.  
 
Los datos personales anteriores y todos aquellos que se pudieran desprender de la entrega de los documentos anteriormente

## Escenario 3: temperatura alta

- `chunk_size`: 1000
- `chunk_overlap`: 200
- `k`: 6
- `temperature`: 0.8
- Chunks generados: 35

### Respuesta

Respuesta general (no proviene del documento):  
La capital de Túnez es Túnez. Es la ciudad principal y sede del gobierno del país.

### Fragmentos recuperados

#### Fragmento 1 — página 8

ANEXO A 
 
TIENDAS 
 
1. C&C Queretaro: Plaza Zimapán #234 Plazas del Sol 3ra Sección, Delegación Josefa 
Vergara y Hernandez C.P. 76099, Queretaro, Queretaro. 
 
2. C&C Celaya: Av., Constituyentes Esq.  Con Antonio Plaza #419 Centro, C.P. 38090, 
Celaya Gto. 
 
3. C&C Cortazar: Fco. I Madero #109, Centro, C.P. 38300, Cortazar, Gto. 
 
4. Autoservicio Jaral: José María Morelos #228, Centro, C.P. 38470, Jaral del Progreso, Gto

#### Fragmento 2 — página 5

responsabilidad por cualquier falla técnica o un funcionamiento defectuoso o cualquier otro 
problema con la red que es té conectado en línea al sistema, servidores, o proveedores de 
otro tipo, que puede ser el resultado de cualquier contenido o entrada en la promoción que 
no esté correctamente registrado. Todas las cuestiones y controversias serán sometidas a 
la decisión final del mismo. 
- La Organizadora no se hace cargo de los gastos que generen, suministro de energía 
eléctrica, servicio de telecomunicaciones, programas y software y hardware, reproductores 
musicales, ni recomienda o promueve marca alguna de insumos tecnológicos y cualquier 
otro requisito de participación. 
- Todos los participantes que  acepten las bases, términos y condiciones de la promoción, 
aceptan en forma adicional, que los mismos puedan ser modificados por los organizadores 
así como de las decisiones que adopten sobre cualquier cuestión prevista o no prevista en

#### Fragmento 3 — página 1

BASES Y MECÁNICAS DE LA PROMOCIÓN 
 
“SU PARTICIPACIÓN EN LA PRESENTE PROMOCIÓN COMERCIAL, CONSTITUYE SU 
ADHESIÓN Y ACEPTACIÓN SIN RESERVA ALGUNA DE LOS PRESENTES TÉRMINOS, 
CONDICIONES, RESTRICCIONES Y AVISO DE PRIVACIDAD, POR LO QUE LE 
RECOMENDAMOS QUE ANTES DE PARTICIPAR LAS LEA CUIDADOSAMENTE A FIN DE QUE 
LAS ANALICE Y CONCIENTEMENTE PARTICIPE O SE ABSTENGA DE ELLO. 
 
Nombre de la promoción: “Ofertas de Hoy con Inés Básicos” 
 
Responsable y organizadora de la promoción: Desarrollo Comercial Abarrotero SA de CV. Con 
domicilio carr. cortazar-estacion km 1.5 s/n predio Santa Anita c.p 38300 Cortazar, Gto 
 
 
Cobertura Geográfica: Nacional, a través de todas las tiendas Básicos (ver anexo A para identificar 
las tiendas). 
 
Vigencia: Del 01 de febrero al 15 de marzo de 2019. 
 
Tiendas participantes: Las tiendas Basicos  de la República Mexicana  que emitan un ticket de 
compra formal siempre y cuando contenga los siguientes elementos: 
 
• Número de ticket

#### Fragmento 4 — página 5

- Si por cualquier razón, la promoción no es capaz de ejecutarse tal y com o estaba previsto, 
incluyendo, alguna limitación, la infección por virus de computadora, bugs, la manipulación, 
intervención no autorizada, el fraude, fallas técnicas o cualquier otra causa corrupta o que 
afecte a la administración, seguridad, equidad, int egridad o la correcta realización de la 
promoción, Desarrollo Comercial Abarrotero ., sus subsidiarias y/o afiliadas se reservan el 
derecho, a su sola discreción para cancelar, demorar, modificar o terminar la promoción; 
previo aviso al público y siempre y cuando no afecte los derechos de los participantes. 
- Desarrollo Comercial Abarrotero., y sus subsidiarias y/o afiliadas no aceptan ninguna 
responsabilidad por cualquier falla técnica o un funcionamiento defectuoso o cualquier otro 
problema con la red que es té conectado en línea al sistema, servidores, o proveedores de

#### Fragmento 5 — página 6

AVISO DE PRIVACIDAD 
1. Identidad y Domicilio del Responsable de sus Datos Personales.  
 
Desarrollo Comercial Abarrotero SA de CV  en lo sucesivo “DECASA” con domicilio en CARR. CORTAZAR -ESTACION 
KM 1.5 S/N PREDIO SANTA ANITA C.P 38300 CORTAZAR, GTO, será responsable del uso, tratamiento y protección de sus 
datos personales en términos de la Ley Federal de Protección de Datos Personales en Posesión de los Particulares.  
Así mismo, le informamos que de ninguna manera manejamos datos sensibles; por tal razón, deberá abstenerse de 
proporcionar datos de esa índole.  
 
2. Datos personales recabados.  
En virtud de su participación en la promoción desplegada, en lo sucesivo “la promoción”, de la cual es responsable DECASA 
con domicilio en CARR. CORTAZAR-ESTACION KM 1.5 S/N PREDIO SANTA ANITA C.P 38300 CORTAZAR, GTO 
 
a) Para participar en la Promoción, Usted deberá proporcionar la siguiente información personal, en términos de las Bases de 
la Promoción:

#### Fragmento 6 — página 6

a) Para participar en la Promoción, Usted deberá proporcionar la siguiente información personal, en términos de las Bases de 
la Promoción:  
 
- Nombre completo (nombre(s), apellido paterno y apellido materno)  
- Correo electrónico  
- Teléfonos de contacto (casa/móvil)  
- Ticket de compra  
- Estado  
 
b) En caso de resultar ganador de la Promoción, confo rme las Bases, deberá presentar y entregar físicamente la siguiente 
documentación:  
 
- Copia de identificación oficial vigente con fotografía por ambos lados.  
- Domicilio completo 
 
Los datos personales anteriores y todos aquellos que se pudieran desprender de la entrega de los documentos anteriormente 
descritos, serán denominados en conjunto y en lo sucesivo “datos personales”. Asimismo, NO recabamos datos personales 
sensibles.  
 
Los datos personales anteriores y todos aquellos que se pudieran desprender de la entrega de los documentos anteriormente

## Análisis de los resultados

### 1. Beneficios y limitaciones del escenario base

En el escenario base, los fragmentos de 1000 caracteres con un traslape de 200 conservaron suficiente contexto alrededor de cada regla. Esto permitió recuperar en un mismo fragmento la causal de descalificación y su explicación, reduciendo el riesgo de interpretar frases aisladas. El traslape también ayudó a preservar ideas que se encontraban cerca del límite entre dos chunks.

La principal limitación es que los fragmentos largos pueden incluir información que no responde directamente a la pregunta. Además, el traslape produce contenido repetido, aumenta la cantidad de texto almacenado y puede hacer que varios resultados contengan partes similares. Aun así, para este documento, la configuración base ofreció un equilibrio adecuado entre contexto y precisión.

### 2. Efecto de chunks pequeños, menor traslape y k=2

Al reducir el chunk_size a 350, el chunk_overlap a 20 y k a 2, los fragmentos fueron más específicos, pero perdieron continuidad. La respuesta recuperó el incumplimiento de los requisitos y los intentos de alterar los sistemas asociados a la promoción, pero omitió otras causales presentes en el PDF, como el fraude, los participantes no elegibles, las violaciones de la dinámica, los hackers y los caza promociones.

Esto muestra que los chunks pequeños pueden mejorar la precisión local, pero un k bajo ofrece muy poco contexto para preguntas que requieren reunir una lista distribuida en varias páginas. En este caso, la respuesta fue menos exacta por incompleta, no porque las afirmaciones recuperadas fueran incorrectas.

### 3. Comparación entre temperature=0.1 y temperature=0.8

Con temperature=0.1, la respuesta fue más directa, estable y cercana a la redacción de los fragmentos. Esta configuración es preferible para términos y condiciones, políticas, contratos y otros documentos donde importa más la fidelidad que la variedad de expresión.

Con temperature=0.8, la respuesta tuvo una redacción más elaborada y desarrolló con mayor amplitud algunas consecuencias. Aunque en esta ejecución se mantuvo respaldada por el contexto, una temperatura alta aumenta la variación entre ejecuciones y el riesgo de agregar interpretaciones no explícitas. Sería más útil para tareas creativas o de estilo, pero no es la opción recomendada para este RAG documental.

## Conclusión

Para esta consulta, el escenario 2 ofrece la respuesta más completa: conserva chunks amplios, mantiene un traslape suficiente, recupera seis fragmentos y utiliza una temperatura baja. El escenario base también funciona bien, mientras que el escenario 1 pierde causales importantes y el escenario 3 introduce una variación de estilo innecesaria para un documento normativo.

## Nota sobre el proveedor

El taller fue ejecutado con OpenAI, conservando el flujo RAG solicitado: carga, división, embeddings, almacenamiento vectorial, recuperación y generación de la respuesta. Los modelos utilizados fueron `text-embedding-3-small` y `gpt-4.1-mini`.
