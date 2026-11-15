# Output template for the company brief

Contents: the brief, the no-access reply, the check list.

## The brief

Use these headings in this order. Leave out a heading only when you say why under Not found.

```markdown
## Project NAME: company brief (draft for review)

**Status:** STAGE, changed on DATE; OPEN or CLOSED [Salesforce ID]
(If closed: "Closed: REASON" first, and no open items below.)

**Company:** one or two lines on what it does. [SharePoint path]

**Key contacts**
- Name, title [contact record ID]

**Financials and customers** (say who supplied them, and whether audited)
- FY revenue, EBITDA [path]
- Customer concentration [path]

**Open diligence items**
- Item, due date [task record ID]
(If none: "None open in Salesforce.")

**Last three interactions** (newest first)
- DATE, type, subject [activity record ID]

**Unverified**
- Fact, both figures if sources disagree, each with its source, and why it is not stated as fact

**Not found**
- What is missing, in plain words, and what to add

Draft only. A reviewer checks every brief before it is used.
```

Fill only what the files support. An empty section says so; it is never padded.

## The no-access reply

Short, with no deal content:

> You do not have access to Project NAME in Salesforce or SharePoint, so I cannot prepare a brief. Please ask the deal owner or IT to review your access, and ask me again once it is changed.

## Check list before presenting

- [ ] About 450 words or fewer.
- [ ] Stage, stage date and open or closed come from the Salesforce record.
- [ ] Every fact has a bracketed source link.
- [ ] Disagreeing or unsupported figures are under Unverified, not in the body.
- [ ] Missing material is named under Not found.
- [ ] No web content, no figure from general knowledge, nothing written or saved.
