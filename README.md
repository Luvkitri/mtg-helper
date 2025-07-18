# mtg-helper

This API provides functionality for finding mtg cards that are similar to the given one. It also has auto-completition
logic for easier card access.

## How does it work?

### Similar cards

Whole retrieval procedure is based on inverted index build from every unique card's text. The api accepts queries in
form of MTG card names. Then using [vector model](https://en.wikipedia.org/wiki/Vector_space_model) the degreee of
similarity is calculated which is used to create a ranking of most similar cards.

### Autocompletition

Autocompletiotion is based on Trie data structure and levenshtein distance. In first step the list of possible
completitions is returned from trie traversal (which is limited to 10 results). Then the list is sorted by the
levenshtein distance of current query and possible result.

## Example

Simple example of this API usage can be found here:
[https://github.com/Luvkitri/mtg-helper-frontend-example](https://github.com/Luvkitri/mtg-helper-frontend-example)


## Running it locally

### Update/Get the data
Run the `get_data.sh` script to download the latest AllPrintings database.

```sh
./scripts/get_data.sh
```
