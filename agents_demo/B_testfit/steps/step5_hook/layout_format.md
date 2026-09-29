# Layout file format

```json
{"buildings": [
  {"id": "A", "type": "slab", "x": 8, "y": 9, "storeys": 4, "rotated": false}
]}
```
- `type` is `tower`, `slab` or `short`.
- `x`, `y` is the south-west corner of the footprint, in the same coordinates as `lot.json`.
- `rotated: true` swaps the two footprint sides (a slab becomes 12 wide and 40 deep).
