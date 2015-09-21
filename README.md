#AD SIM

### Fake users send logs to a fake ad server




In `simulate_behavior`, a population of users generate preferences among a set of brands.

They browse along through the brands' products and, if shown an ad, will either like the brand more (if already predisposed) or like them less (if truly an 'unqualified audience'). Each brand has its own normal distribution describing its product mix.

Every once in a while, a user will consider purchase. If their brand preferences are low variance, they'll leave without buying. If their brand preferences are high variance, they'll buy their favorite brand.

The tracking server, `receiver`, records user information in redis and decides whether to display an ad on each page. Showing an ad before being confident the user likes a brand risks turning them off the brand. Not showing ads means the users' preferences will likely remain low variance and they'll leave without purchasing.

##### Can you maximize the revenues??