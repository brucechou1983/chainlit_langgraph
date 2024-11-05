#!/bin/bash
# poetry update

# Update the version numbers in the README.md file
CHAINLIT_VERSION=$(poetry show chainlit | grep 'version' | awk '{print $NF}')
echo "Updating Chainlit version to ${CHAINLIT_VERSION}"
sed -i '' "s/Chainlit-[0-9]*[.][0-9]*[.][0-9]*/Chainlit-${CHAINLIT_VERSION}/" README.md

LANGGRAPH_VERSION=$(poetry show langgraph | grep 'version' | awk '{print $NF}')
echo "Updating LangGraph version to ${LANGGRAPH_VERSION}"
sed -i '' "s/LangGraph-[0-9]*[.][0-9]*[.][0-9]*/LangGraph-${LANGGRAPH_VERSION}/" README.md