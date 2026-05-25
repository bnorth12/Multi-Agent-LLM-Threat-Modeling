# L0 Aircraft Functional Baseline

## Canonical L0 Functions

1. Aviate
1. Navigate
1. Communicate
1. Operate

## L0 Intent Definitions

### Aviate

Maintain controlled flight and execute maneuvering while sustaining airworthiness-critical services.

### Navigate

Determine position, plan and manage route/trajectory, and guide movement to mission destination.

### Communicate

Exchange operational information with crew, systems, air/ground entities, and mission stakeholders.

### Operate

Deliver aircraft purpose-specific operational outcomes beyond core flight and navigation.

## Variant Rule for Operate

- Passenger aircraft emphasize transport service and passenger-support functions.
- Missionized aircraft emphasize payload/sensor mission execution and intelligence products.

## L0 to L1 Summary

- Aviate: stability/control, maneuvering, automation, and essential flight services.
- Navigate: guidance management, route planning, and navigation sensor management.
- Communicate: voice/data links, networked information exchange, and mission communications.
- Operate: passenger services or mission system operation depending on aircraft purpose.

## Structural View Mapping

Some programs organize the architecture as:

1. Flight Controls
1. Vehicle Management
1. Mission Systems (military) or Passenger Systems (commercial)

In this decomposition, that structural view maps as follows:

- Flight Controls: primarily Aviate and Navigate.
- Vehicle Management: essential flight services plus operational communication infrastructure.
- Mission Systems or Passenger Systems: primarily Operate variant branches.

For military platforms, communication that is military-unique is typically grouped under Mission Systems.
For commercial passenger platforms, communication is typically grouped under Vehicle Management, with Passenger Systems replacing Mission Systems.
