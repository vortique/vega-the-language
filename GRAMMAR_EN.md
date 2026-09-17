# Grammar of the Vega Language

## Data Types

**Numeric/Integer** = `sayisal`

**String** = `dize`

**Boolean** = `bool`

Boolean values are written as `dogru` and `yanlis`.

---

## Variables

**Creating/declaring variables**:

```vtl
sayisal number = 10

dize text = "Hello, world!"

bool trueValue = dogru
bool falseValue = yanlis
```

---

## Built-in Functions

### Adding Comments

```vtl
# This is a comment
```

### Printing Data to the Screen

```vtl
yazdir "Hello, world!"
```

### Reading Data from the User

```vtl
dize name = veri "Your name?"
```

### Calculating Character Count

```vtl
uzunluk "Hello, world!"
```

### Calculating an Absolute Value

```vtl
sayisal ten = mutlak -10
```

### Creating a List

```vtl
liste myList = liste.yeni 1,abc,3.14
```

### Adding Elements to a List

```vtl
myList.ekle "Abc"
myList.ekle 314
myList.ekle "abc",3.14
```

---

## Conditions (`if/elif/else`)

Indentation defines condition blocks. Colons are optional after `eger` and
`ikincil`, but required after `degilse`.

```vtl
sayisal value = veri "Enter a number: "

eger value > 10
    yazdir "No 1"
ikincil value < 0
    yazdir "No 2"
degilse:
    yazdir "No 3"
```

---

## Defining and Calling Functions

Indentation defines the function body. Parameters are declared between `/`
characters with their types and names.

```vtl
belirle HelloWorld/dize message, dize description/
    yazdir message
    yazdir description

HelloWorld/"Hello, world!", "Greetings from Vega!"/

# Alternative call syntax
HelloWorld "Hello, world!", "Greetings from Vega!"
```

---

## Error Handling

Runtime errors in the `dene` block cause the `yakala` block to run.

```vtl
dene:
    x = "Hello World!"
yakala:
    yazdir "Error!"
```

---

## Coming Soon

### Printing Version Information

```vtl
yazdir surum
```
