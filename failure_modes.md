## Failure Mode 1: Order Not Found
Agent attempts email lookup → fails → asks user for order ID

## Failure Mode 2: Refund Tool Failure
Agent catches exception → escalates with full context

## Failure Mode 3: Ambiguous Query
Agent asks for clarification instead of acting

## Failure Mode 4: Fraud Attempt
Agent detects mismatch in customer tier → blocks request