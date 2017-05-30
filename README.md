Build Status (branch specific): ```{r, echo=FALSE, eval=TRUE, results="asis"}
travis_url <- "https://travis-ci.org/autodrive/f2py.svg?branch="
shield <- paste0("[![Build Status](",
                 travis_url,
                 system("git rev-parse --abbrev-ref HEAD", intern = TRUE),
                 ")](https://travis-ci.org/autodrive/f2py)")
cat(shield)
```