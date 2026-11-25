# shipcalc

Works out the delivery charge for an order in our online shop.

## The rules

- Orders of 50.00 or more are delivered free.
- Smaller orders pay a flat charge of 4.95.
- Express delivery adds 6.00 on top, whatever the order size.

## Use

    node bin/shipcalc.js 42.50
    node bin/shipcalc.js 80 --express

## Tests

    npm test
