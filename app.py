#!/usr/bin/env python3

from aws_cdk import core

from cfrepo.cfrepo_stack import CfrepoStack


app = core.App()
CfrepoStack(app, "cfrepo")

app.synth()
