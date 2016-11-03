#! /bin/sh

PYGLETV=1.2.4
PYGLETPATH=./lib/pyglet
BUILDPATH=/tmp/gfolf/

# test for python3
if [[ -z $(which python3 2>/dev/null) ]]; then
    echo "python3 is either not installed or not in your path. You are not cool enough to GFOLF, sry."
    exit 1
fi

# extract and build pyglet
if [ ! -d $PYGLETPATH ]; then
    echo "couldn't find pyglet python3 libs. If you are a first-time GFOLFer, we just need to build the pyglet lib real quick..."
    echo "extracting to $BUILDPATH..."
    mkdir -p $BUILDPATH
    tar -xzf lib/pyglet-$PYGLETV.tar.gz -C $BUILDPATH
    echo "building pyglet for python3..."
    (cd $BUILDPATH/pyglet-$PYGLETV; python3 setup.py build >/dev/null)
    echo "installing locally in $PYGLETPATH..."
    mv $BUILDPATH/pyglet-$PYGLETV/_build/lib/pyglet $PYGLETPATH
    echo "tidying up..."
    rm -rf $BUILDPATH
    echo "we're done-ion rings."
fi

echo "setup looks good. rock 'n roll..."

set PYTHONPATH $PYGLETPATH:$PYTHONPATH
export PYTHONPATH

python3 gfolf.py
