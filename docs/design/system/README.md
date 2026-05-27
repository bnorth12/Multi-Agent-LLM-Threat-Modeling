# System Design Documents

This folder is reserved for system-level design documents that elaborate deployment topology, external integrations, operational control loops, and end-to-end data exchange behavior.

System design documents should answer what an operator, integrator, or release engineer needs to know about running the product as a whole, rather than how one internal module is coded.

Current contents:

| Document | System question it answers |
|---|---|
| `External_Interface_And_Integration_Design_Package.md` | What crosses the system boundary and how those integrations are controlled. |
| `System_Deployment_And_Operating_Modes_Design.md` | How the product is deployed, packaged, and operated across supported modes. |

Planned additions include:

- Additional operational deployment detail only if release or fielding complexity exceeds the current design package.
- Additional release-evidence packaging detail only if the software and system packaging authorities need to be separated further.
