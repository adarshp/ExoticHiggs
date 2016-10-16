Signals to generate
===================

- A -> H+ W-
- A -> HZ
- A -> hZ
- H -> AA
- H -> H+ H-
- H -> hh
- H -> H+ W-
- H+ -> AW+
- H+ -> H W+
- H+ -> hW+

Backgrounds to generate
=======================

- ttbar + 2j - fully leptonic 
- Zbb, Z leptonic
- h_SM Z

MG5 generation syntax for different backgrounds
===============================================

Common to all processes: import model 2HDM_HEFT (or loop_2HDM with MG5@NLO and
MadSpin decays.)

1. A -> HZ
  generate g g > h3 , ( h3 > h2 z , h2 > b b~ , z > l+ l- )

  generate g g > h3 , ( h3 > h2 z , h2 > b b~ , z > ta+ ta- )
2. 

There are others, but let's focus on them later. We can input them by hand in the code.


I've modified my previous event generation code so that we can easily create signal processes corresponding to different benchmark planes

Now to implement automated cluster generation.

Also, implement the passing of flags to the python code to do different things.
Also, a help function
