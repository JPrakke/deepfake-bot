# Creates a deploy.zip package that can be uploaded to EBS. Then versions and tags it in .git. This assumes any code changes have already been tested and committed.


# BUILD -- really just copies the needed files and zips them up.

echo "Deleting old files..."
rm -r cogs/__pycache__
rm deploy.zip

echo "Creating package..."
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

MAJOR_VERSION=1 # <---to make a major or minor release these should be edited and committed
MINOR_VERSION=0
PATCH_VERSION=6

echo "Tagging in git..."
git tag v$MAJOR_VERSION.$MINOR_VERSION.$PATCH_VERSION

echo "Preparing for next release..."
NEW_PATCH_VERSION=$((PATCH_VERSION+1))

# Edit this script in place with the next version number. Sort of dangerous but it's only a small change.
increment() {
    local search="PATCH_VERSION=$PATCH_VERSION"
    local replace="PATCH_VERSION=$NEW_PATCH_VERSION"
    sed -i "0,/${search}/s/${search}/${replace}/" release.sh
}

increment

echo "Committing..."
git add release.sh
git commit -m "RELEASE SCRIPT: preparing for next release"

echo "Pushing..."
git push
git push --tags

echo "Release complete!"
