#!/bin/bash


pubget run -q "(elephant[Abstract] AND brain[Abstract]) AND (2021[PubDate] : 2022[PubDate])" \
    --labelbuddy                                              \
    .