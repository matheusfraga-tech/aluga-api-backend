
## 1️⃣ Visão Geral

O endpoint de **search** permite que os usuários busquem hotéis aplicando diversos filtros e ordenações, considerando tanto características do hotel (nome, cidade, bairro, opções disponíveis de lazer) quanto aspectos dinâmicos de disponibilidade e preço de quartos. Ele deve fornecer resultados confiáveis, refletindo a **disponibilidade real para o período desejado**, apresentando preços corretos e oferecendo mecanismos de ordenação relevantes para a tomada de decisão do usuário.

O público-alvo principal da plataforma são:

- Turistas de lazer, que buscam acomodações próximas a pontos de interesse ou atrações da cidade.
- Famílias e grupos pequenos, que necessitam de quartos compatíveis com a quantidade de pessoas.
- Viajantes a trabalho, que priorizam praticidade, custo-benefício e proximidade de centros de interesse ou corporativos.

A complexidade do endpoint vem da necessidade de conciliar filtros estáticos (nome, cidade, amenities) com filtros e ordenações **dinâmicas** (preço real disponível, distância, popularidade).

---

## 🔑 Princípio da Ordenação (`sort`)

A busca de hotéis adota o modelo de **ordenação exclusiva por critério**.  
Isso significa que, em cada requisição, o usuário pode escolher **apenas um critério de ordenação ativo por vez**.

- Valores possíveis:

- `price` → ordena pelos preços disponíveis no período selecionado.
- `rating` → ordena pela nota média (`stars`).
- `popularity` → ordena pelo nível de procura (`popularity_score`).
- `distance` → ordena pela proximidade do ponto de interesse (`user_lat`, `user_lng`).
- `id` → ordenação padrão (fallback).

- **Implicações de negócio:**

- Os critérios são **mutuamente exclusivos**. Ex.: não é possível ordenar ao mesmo tempo por `distance` e `price`.

- Essa decisão segue práticas consolidadas do mercado de turismo (Booking, Expedia, Hoteis.com), privilegiando **clareza para o usuário final**.

- Caso no futuro seja necessário oferecer múltiplos critérios (ex.: distância como primário e preço como secundário), isso poderá ser evoluído na API, mas atualmente **o modelo prioriza simplicidade e previsibilidade**.

### 📌 Exemplos de uso do `sort`

#### Exemplo 1: Ordenação por preço

```http
GET /hotels/search?city=Belo%20Horizonte&check_in=2025-12-20&check_out=2025-12-25&sort=price
```

- Resultado: hotéis ordenados do **mais barato ao mais caro**, considerando apenas os quartos **disponíveis** no período solicitado (`min_price_available`).

- Neste modo, não há influência de `distance`, `rating` ou `popularity`.


---

#### Exemplo 2: Ordenação por distância

```http
GET /hotels/search?city=Rio%20de%20Janeiro&user_lat=-22.9068&user_lng=-43.1729&sort=distance
```

- Resultado: hotéis ordenados do **mais próximo ao mais distante** do ponto de interesse informado.

- Exemplo prático: se o usuário escolheu ficar próximo ao **Cristo Redentor**, os hotéis mais perto aparecem no topo.

- Outros critérios (como preço ou rating) não participam da ordenação.


---

#### Exemplo 3: Ordenação por popularidade

```http
GET /hotels/search?city=São%20Paulo&sort=popularity
```

- Resultado: hotéis ordenados pelo **nível de procura** (reservas recentes, cliques, reviews).

- Útil para destacar os “queridinhos” da plataforma.


---

#### Exemplo 4: Ordenação por rating (estrelas)

```http
GET /hotels/search?city=Curitiba&sort=rating
```

- Resultado: hotéis ordenados do **melhor avaliado ao pior**.

- Baseado na conversão de reviews para uma escala de 0–5 estrelas (`stars`).



📌 **Resumo importante**: cada requisição aceita **somente um critério de ordenação por vez**. Se o cliente enviar um valor inválido ou tentar combinar critérios, a API retorna erro de validação.

----

## 2️⃣ Filtro e Ordenação por Distância (`distance`)

- **Quando usar**:  
Apenas se o usuário fornecer **coordenadas de destino** (lat/lng) do local desejado, como o centro da cidade ou ponto turístico.

- **Como funciona**:

- A distância é calculada via **Haversine** entre o ponto de interesse e cada hotel.

- A unidade utilizada é **km**.

- **Regras de negócio**:

- Se o usuário não fornecer `user_lat` ou `user_lng`, **não é permitido ordenar ou filtrar por distância**.

- Distância deve ser usada apenas para ordenação ou ranking, não para definir disponibilidade ou preço.

**Observação importante:** O filtro não deve ser baseado na localização do usuário residencial; o foco é sempre o **destino da estadia**:

Uso prático ✅

O usuário quer viajar para **Porto Seguro – BA** e coloca como referência o **Aeroporto Internacional de Porto Seguro (lat/lng)**.

- A API calcula a distância entre cada hotel cadastrado em Porto Seguro e o aeroporto.

- Isso ajuda o usuário a escolher hotéis mais próximos do aeroporto, da praia ou de outro ponto turístico que ele indicar.

Uso não prático ❌

O usuário mora em **Embu das Artes – SP** e informa sua casa como `user_lat`/`user_lng`.

- O sistema calcularia a distância entre a casa dele e os hotéis em Porto Seguro.

- Isso não tem valor algum para a decisão, já que ele não vai se hospedar em Embu e a viagem de avião já resolve a questão do deslocamento.

- **Documentação para API**:


> `distance_km`: distância do hotel ao ponto de interesse (`user_lat`/`user_lng`). Ordenação por distância só funciona se coordenadas forem fornecidas.

---

## 3️⃣ Filtros de Período (`check_in` / `check_out`)

- **Objetivo:**  
    Permitir que o cliente busque hotéis disponíveis para um período específico de estadia. Esses filtros são essenciais para determinar **a disponibilidade real de quartos** e influenciam diretamente outros filtros e ordenações (preço, ordenação por preço).
    
- **Regras de Negócio:**
    
    1. O `check_out` deve ser sempre posterior ao `check_in`.
        
    2. A busca deve considerar **reservas já confirmadas** e o campo `total_units` de cada quarto, garantindo que apenas quartos efetivamente disponíveis apareçam nos resultados.
        
    3. Quando o usuário **não informa datas**, o sistema pode retornar hotéis com base na disponibilidade geral, mas preços e ordenação por preço não refletem necessariamente a realidade do período desejado.
        
    4. Filtros e ordenações dependentes do período:
        
        - **Filtros de preço** (`price_min` / `price_max`)
            
        - **Ordenação por preço** (`sort=price`)
            

---

## 4️⃣ Filtro por Faixa de Preço (`price_min` / `price_max`) e Disponibilidade

- **Problema:**  
    Usar apenas o `base_price` do quarto pode gerar informações enganosas se os quartos mais baratos não estiverem disponíveis no período solicitado.
    
- **Solução:**  
    Definir **dois preços mínimos distintos**:
    

1. **`min_price_general`**
    
    - Menor preço entre todos os quartos do hotel, **sem considerar datas**.
        
    - Funciona como referência geral para o cliente, mostrando o valor mais baixo que o hotel historicamente oferece.
        
    - **Exibição:** apenas informativo.
        
2. **`min_price_available`**
    
    - Menor preço considerando **somente quartos disponíveis** no período solicitado (`check_in` / `check_out`).
        
    - **Uso:** filtros (`price_min` / `price_max`) e ordenação por preço (`sort=price`).
        
    - **Cálculo:** leva em conta `total_units` do quarto e reservas já existentes.
        

- **Regras de Negócio:**
    
    - `price_min` / `price_max` e `sort=price` **devem usar `min_price_available`** quando datas forem informadas.
        
    - Se **nenhuma data for informada**, usar **`min_price_general`** de forma **informativa**, indicando que a disponibilidade real não foi considerada.
        
    - Outros filtros (`room_type`, `amenities`, `city`, `neighborhood`) funcionam normalmente, mesmo sem datas.
        
    - `distance`, `stars` e `popularity` podem ser utilizados independentemente das datas.
        

---

## 5️⃣ Ordenação por Preço (`sort=price`)

- **Objetivo:**  
    Permitir que o usuário visualize hotéis do mais barato ao mais caro (ou vice-versa), considerando o período desejado.
    
- **Regras de Negócio:**
    
    1. **Com datas informadas:** ordenar pelo `min_price_available`.
        
    2. **Sem datas informadas:** ordenar pelo `min_price_general`.
        
        - Exibição deve indicar que os preços são **referenciais**, sem garantia de disponibilidade.
            
        - Sugestão de aviso no frontend:
            
            > “Preço baseado em valores gerais. Disponibilidade para datas específicas não confirmada.”
            
    3. A ordenação deve ser aplicada **após todos os filtros já aplicados** (ex.: `city`, `room_type`, `amenities`).
        

---

## 6️⃣ Cenários de uso sem datas (`check_in` / `check_out` não informadas)

1. **Filtragem por faixa de preço**
    
    - `price_min` / `price_max` utiliza **`min_price_general`**.
        
    - Resultado pode incluir hotéis sem quartos disponíveis naquele valor.
        
    - Exibir aviso ou badge indicando que a disponibilidade real não foi considerada.
        
2. **Ordenação por preço**
    
    - Considera **`min_price_general`**.
        
    - Recomenda-se incentivar o usuário a informar datas para obter ordenação e preços reais.
        
3. **Combinação de filtros e ordenação**
    
    - `price_min` / `price_max` + `sort=price` → usa `min_price_general`.
        
    - Outros filtros (`room_type`, `amenities`, `city`, `neighborhood`, `distance`, `stars`, `popularity`) continuam funcionando normalmente.
        

---

### ✅ Comportamento sugerido no frontend

- Exibir **`min_price_general`** no card do hotel.
    
- Exibir tooltip ou badge indicando que **a disponibilidade real para datas não foi considerada**.
    
- Incentivar o usuário a informar `check_in` / `check_out` para habilitar:
    
    - Filtros de preço precisos (`min_price_available`)
        
    - Ordenação correta por preço
        
    - Garantia de que o preço exibido pode ser reservado efetivamente.
        

---

## 4️⃣ Tipos de Quartos (`room_type`)

- **Objetivo**:  
Padronizar categorias de quartos com base **na quantidade de leitos**, facilitando filtros, busca e comparação.

- **Enum padrão sugerido**:


|Tipo|Capacidade típica|Observação|
|---|---|---|
|Single|1 hóspede|Ideal para viajantes individuais|
|Double|2 hóspedes|Casais ou duplas|
|Triple|3 hóspedes|Pequenos grupos ou famílias pequenas|
|Quadruple|4 hóspedes|Famílias médias|
|Family|4+ hóspedes|Flexibilidade para famílias maiores|

- **Regras de negócio**:

- Ao cadastrar quartos, o sistema **mapeia o nome do quarto do hotel para uma categoria do enum**.

- O filtro `room_type` **refina a busca** sem anular outros filtros como preço, datas ou amenities.

- Evita frustração do usuário ao garantir que quartos exibidos tenham capacidade compatível com o número de hóspedes desejado.

- Não se considera alocação de imóveis inteiros com múltiplos quartos, pois isso corresponde a outro nicho de mercado (tipo Airbnb).

- **Documentação para API**:


> `room_type`: categoria do quarto (`Single`, `Double`, `Triple`, `Quadruple`, `Family`). Opcional, refina busca dentro do conjunto de hotéis que atendem aos demais filtros.

---

## 5️⃣ Resumo de Filtros e Ordenações

| Filtro / Ordenação        | Regras de negócio                                            | Observações                                           |
| ------------------------- | ------------------------------------------------------------ | ----------------------------------------------------- |
| `q` (nome do hotel)       | Busca parcial (`LIKE`) no nome                               | Opcional                                              |
| `city` / `neighborhood`   | Busca parcial no nome da cidade/bairro                       | Opcional                                              |
| `amenities`               | Verifica se o hotel possui todas as amenities selecionadas   | Opcional                                              |
| `room_type`               | Categoria padrão (Single, Double, Triple, Quadruple, Family) | Refina busca; não anula outros filtros                |
| `price_min` / `price_max` | Calculado sobre `min_price_available`                        | Considera disponibilidade real no período             |
| `check_in` / `check_out`  | Define período de reserva                                    | Necessário para cálculo de `min_price_available`      |
| `distance`                | Calculado via Haversine a partir do ponto de interesse       | Ordenação só se coordenadas fornecidas                |
| `stars`                   | Pontuação aproximada para exibição (0–5)                     | Baseado em avaliações de usuários; útil para frontend |
| `popularity`              | Indicador de demanda / interesse                             | Baseado em reservas, reviews, métricas de engajamento |

---

## 6️⃣ Detalhamento de `stars` e `popularity`

### 6.1 Stars (Média de Avaliações)

- **Objetivo:** Exibir uma **representação visual da qualidade do hotel** (escala 0–5 estrelas) no frontend.
    
- **Como calcular:** É a **média aritmética** direta das notas de avaliações (`rating`) dos usuários.
    
- Fórmula na Implementação:
    
    $$\text{Stars} = \text{Arredondar}(\frac{\sum \text{rating}}{\text{Nº Total de Reviews}}, 1)$$
    
    Python
    
    ```
    calculated_stars = round(avg_rating_result, 1)
    ```
    
- **Regras de Negócio:**
    
    - **Atualizado** imediatamente quando novas avaliações são feitas, atualizadas ou excluídas.
        
    - Serve como **indicador visual** da qualidade do hotel, não é o fator principal na ordenação complexa.
        

---

### 6.2 Popularity (Métrica de Engajamento e Relevância)

- **Objetivo:** Indicar **quão procurado e relevante** o hotel é, refletindo sua demanda e engajamento.
    
- **Como calcular:** É uma pontuação ponderada que combina **reservas recentes**, o **volume de reviews** e a **média de estrelas** (`stars`).
    
- Fórmula na Implementação:
    
    $$\text{Popularidade} = (0.5 \times \text{Bookings}_{30d}) + (0.3 \times \text{Total Reviews}) + (0.2 \times \text{Stars})$$
    
    Python
    
    ```
    popularity_score = round(
        (0.5 * bookings_count) + 
        (0.3 * total_reviews) + 
        (0.2 * stars_score), 
        1
    )
    ```
    
- **Regras de Negócio:**
    
    - Diferente de `stars`, reflete **demanda e engajamento**, não apenas qualidade.
        
    - O cálculo é ativado a cada nova **reserva** ou **review** feita/atualizada.
        
    - Usado principalmente para **ordenar e destacar resultados** na busca, priorizando hotéis ativos.
        

---

### 6.3 Diferença prática entre `stars` e `popularity`

|**Aspecto**|**Stars**|**Popularity**|
|---|---|---|
|**Fonte**|Apenas a **nota** das avaliações (rating).|**Volume** de Reviews + **Média** de Reviews + **Bookings Recentes**.|
|**Escala**|0–5 (Visual).|Métrica **interna** (Float), sem limite máximo prático.|
|**Foco**|Qualidade percebida.|Relevância e demanda (engajamento).|
|**Atualização**|Após cada evento de Review.|Após cada evento de Review **ou** Booking.|
|**Uso na Interface**|Visual (exibição de estrelas) e filtro de qualidade.|**Ordenação** (ranking) e destaque de hotéis ativos.|

---

## 7️⃣ Considerações Finais

- **Min_price_available** garante que o usuário **não seja enganado** por preços de quartos indisponíveis.

- **RoomTypeEnum** padroniza quartos e facilita a filtragem para a **maior parte do público-alvo**, sem precisar lidar com casos irrealistas.

- **Distance filter** é opcional e só aplicável quando coordenadas do destino forem fornecidas.

- **Stars e popularity** são indicadores separados, permitindo uma **visualização rápida da qualidade** e do **nível de procura** do hotel, auxiliando na decisão de reserva.

