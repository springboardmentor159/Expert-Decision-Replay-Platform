import axiosClient from "../api/axiosClient";

// Get repository decisions
export const getRepositoryDecisions = async (params = {}) => {
  const response = await axiosClient.get("/decisions", {
    params,
  });

  return response.data;
};


// Get all tags
export const getTags = async () => {
  const response = await axiosClient.get("/tags");

  return response.data;
};


// Get a specific tag
export const getTag = async (tagId) => {
  const response = await axiosClient.get(
    `/tags/${tagId}`
  );

  return response.data;
};


// Create tag
export const createTag = async (tagData) => {
  const response = await axiosClient.post(
    "/tags",
    tagData
  );

  return response.data;
};


// Delete tag
export const deleteTag = async (tagId) => {
  const response = await axiosClient.delete(
    `/tags/${tagId}`
  );

  return response.data;
};