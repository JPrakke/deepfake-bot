# Creates a deploy.zip package that can be uploaded to EBS. Then versions and tags it in .git. This assumes any code changes have already been tested and committed.

MAJOR_VERSION=1 # <---to make a major or minor release these should be edited and committed
MINOR_VERSION=2
PATCH_VERSION=0

# BUILD -- Copy the version number from this file into config.py then zip the needed files.

echo "Deleting old files..."
rm -r cogs/__pycache__
rm deploy.zip

echo "Creating package..."

# Copies the version number from this file to config.py
copyversion() {
    local search="version = 'DEVELOPMENT'"
    local replace="version = '$MAJOR_VERSION.$MINOR_VERSION.$PATCH_VERSION'"
    sed -i "0,/${search}/s/${search}/${replace}/" ./cogs/config.py
}

copyversion

mkdir deploy
cp -r cogs deploy
cp -r tmp deploy
cp bot.py deploy
cp Dockerfile deploy
cp Dockerrun.aws.json deploy
cp requirements.txt deploy

cd deploy
zip -r ../deploy.zip *
cd ..

echo "Cleaning up..."
rm -r deploy


# RELEASE -- adds a tag. Then increments the patch number and commits it.

echo "Committing..."
git add ./cogs/config.py
git commit -m "RELEASE SCRIPT: releasing v$MAJOR_VERSION.$MINOR_VERSION.$PATCH_VERSION"

echo "Tagging in git..."
git tag v$MAJOR_VERSION.$MINOR_VERSION.$PATCH_VERSION

echo "Preparing for next release..."

NEW_PATCH_VERSION=$((PATCH_VERSION+1))

# Edit this script in place with the next version number. Sort of dangerous but it's only a small change.
increment() {
    local search="PATCH_VERSION=$PATCH_VERSION"
    local replace="PATCH_VERSION=$NEW_PATCH_VERSION"
    sed -i "0,/${search}/s/${search}/${replace}/" release.sh

    local search="version = '$MAJOR_VERSION.$MINOR_VERSION.$PATCH_VERSION'"
    local replace="version = 'DEVELOPMENT'"
    sed -i "0,/${search}/s/${search}/${replace}/" ./cogs/config.py
}

increment

echo "Committing..."
git add release.sh
git add ./cogs/config.py
git commit -m "RELEASE SCRIPT: preparing for next release"

echo "Tagging self-deployment branch..."
git checkout self-deployment
git tag self-deployment-v$MAJOR_VERSION.$MINOR_VERSION.$PATCH_VERSION

echo "Pushing..."
git push --all
git push origin --tags

echo "Release complete!"
git checkout master
