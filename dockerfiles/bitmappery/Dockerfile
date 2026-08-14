# Written by Ange Cesari
# Use official Node.js based on Alpine
FROM node:24-alpine

# Create dir for application
WORKDIR /usr/src/app

# Copy package.json and the lockfile, so yarn resolves pinned versions rather
# than whatever is newest at build time. The glob keeps the lockfile optional.
COPY package.json yarn.lock* ./

# Install dependencies
RUN yarn install

# Copy the rest of the application code
COPY . .

# Expose the port the application will run on
EXPOSE 5173

# Run the application
CMD ["yarn", "dev", "--host", "0.0.0.0"]
