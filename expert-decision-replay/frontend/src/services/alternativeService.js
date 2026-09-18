import api from "./api";

// Create a new alternative
const createAlternative = async (alternativeData) => {
  const response = await api.post(
    "/alternatives/",
    alternativeData
  );

  return response.data;
};

// Get all alternatives
const getAlternatives = async () => {
  const response = await api.get("/alternatives/");

  return response.data;
};

// Get one alternative by ID
const getAlternativeById = async (alternativeId) => {
  const response = await api.get(
    `/alternatives/${alternativeId}`
  );

  return response.data;
};

// Update an alternative
const updateAlternative = async (
  alternativeId,
  alternativeData
) => {
  const response = await api.put(
    `/alternatives/${alternativeId}`,
    alternativeData
  );

  return response.data;
};

// Delete an alternative
const deleteAlternative = async (alternativeId) => {
  const response = await api.delete(
    `/alternatives/${alternativeId}`
  );

  return response.data;
};

const alternativeService = {
  createAlternative,
  getAlternatives,
  getAlternativeById,
  updateAlternative,
  deleteAlternative,
};

export default alternativeService;