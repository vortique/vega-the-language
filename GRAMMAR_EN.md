# Grammar of the Vega Language

## Data Types

**Numeric/Integer** = `sayisal`

**String** = `dize`

---

## Variables

**Creating/declaring a variable**:

```vtl
sayisal x = 10

dize y = "Hello, world!"
```

---

## Built-in Functions

```vtl

# Adding comments

## Printing data to the screen

yazdir "Hello, world!"

## Reading data from the user

x = veri "Your name?"

## Calculating Character Count

uzunluk "Hello, world!"

## Creating a List

liste myList = liste.yeni 1,abc,3.14

## Adding Elements to a List

myList.ekle "Abc"
myList.ekle 314
myList.ekle "abc",3.14
```
