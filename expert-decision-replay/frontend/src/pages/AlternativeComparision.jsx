import { useEffect, useState } from "react";
import alternativeService from "../services/alternativeService";

import LoadingState from "../components/LoadingState";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";

const AlternativeComparison = () => {
  const [alternatives, setAlternatives] = useState([]);
  const [selectedIds, setSelectedIds] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // --------------------------------------------------
  // FETCH ALL ALTERNATIVES
  // --------------------------------------------------

  useEffect(() => {
    const fetchAlternatives = async () => {
      try {
        setLoading(true);
        setError("");

        console.log("Fetching all alternatives...");

        const response =
          await alternativeService.getAlternatives();

        console.log(
          "Alternatives response:",
          response
        );

        // Backend may return:
        // 1. [...]
        // 2. { alternatives: [...] }
        // 3. { data: [...] }

        let alternativesData = [];

        if (Array.isArray(response)) {
          alternativesData = response;
        } else if (
          Array.isArray(response?.alternatives)
        ) {
          alternativesData = response.alternatives;
        } else if (
          Array.isArray(response?.data)
        ) {
          alternativesData = response.data;
        }

        setAlternatives(alternativesData);
      } catch (err) {
        console.error(
          "Error fetching alternatives:",
          err
        );

        const detail =
          err.response?.data?.detail;

        if (Array.isArray(detail)) {
          setError(
            detail
              .map((item) => item.msg)
              .join(", ")
          );
        } else {
          setError(
            detail ||
              "Failed to load alternatives."
          );
        }

        setAlternatives([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAlternatives();
  }, []);

  // --------------------------------------------------
  // SELECT / UNSELECT ALTERNATIVE
  // --------------------------------------------------

  const handleSelect = (alternativeId) => {
    setSelectedIds((previousIds) => {
      // Unselect
      if (
        previousIds.includes(
          alternativeId
        )
      ) {
        return previousIds.filter(
          (id) =>
            id !== alternativeId
        );
      }

      // Maximum 3 alternatives
      if (previousIds.length >= 3) {
        return previousIds;
      }

      return [
        ...previousIds,
        alternativeId,
      ];
    });
  };

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------

  if (loading) {
    return <LoadingState />;
  }

  // --------------------------------------------------
  // ERROR
  // --------------------------------------------------

  if (error) {
    return <ErrorState message={error} />;
  }

  // --------------------------------------------------
  // EMPTY
  // --------------------------------------------------

  if (alternatives.length === 0) {
    return (
      <EmptyState
        message="No alternatives found."
      />
    );
  }

  // --------------------------------------------------
  // SELECTED ALTERNATIVES
  // --------------------------------------------------

  const selectedAlternatives =
    alternatives.filter(
      (alternative) =>
        selectedIds.includes(
          alternative.id
        )
    );

  // --------------------------------------------------
  // MAIN UI
  // --------------------------------------------------

  return (
    <div className="space-y-6">

      {/* HEADER */}

      <div>
        <h1 className="text-2xl font-bold text-gray-800">
          Alternative Comparison
        </h1>

        <p className="mt-1 text-gray-600">
          Select up to three alternatives
          to compare.
        </p>
      </div>

      {/* ALTERNATIVES */}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">

        {alternatives.map(
          (alternative) => {
            const isSelected =
              selectedIds.includes(
                alternative.id
              );

            return (
              <div
                key={alternative.id}
                className={`rounded-lg border p-4 shadow-sm ${
                  isSelected
                    ? "border-blue-500 bg-blue-50"
                    : "border-gray-200 bg-white"
                }`}
              >

                {/* TITLE + CHECKBOX */}

                <div className="flex items-start justify-between gap-3">

                  <h2 className="text-lg font-semibold text-gray-800">
                    {alternative.title ||
                      alternative.name ||
                      `Alternative ${alternative.id}`}
                  </h2>

                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={() =>
                      handleSelect(
                        alternative.id
                      )
                    }
                    aria-label="Select alternative"
                  />

                </div>

                {/* DESCRIPTION */}

                <p className="mt-3 text-sm text-gray-600">
                  {alternative.description ||
                    "No description available."}
                </p>

                {/* DETAILS */}

                <div className="mt-4 space-y-2 text-sm">

                  <p>
                    <span className="font-medium">
                      ID:
                    </span>{" "}
                    {alternative.id}
                  </p>

                  <p>
                    <span className="font-medium">
                      Cost:
                    </span>{" "}
                    {alternative.cost ??
                      alternative.estimated_cost ??
                      "N/A"}
                  </p>

                  <p>
                    <span className="font-medium">
                      Benefit:
                    </span>{" "}
                    {alternative.benefit ??
                      "N/A"}
                  </p>

                  <p>
                    <span className="font-medium">
                      Risk:
                    </span>{" "}
                    {alternative.risk_level ||
                      alternative.risk ||
                      "N/A"}
                  </p>

                  <p>
                    <span className="font-medium">
                      Score:
                    </span>{" "}
                    {alternative.score ??
                      alternative.feasibility_score ??
                      "N/A"}
                  </p>

                  {alternative.pros && (
                    <p>
                      <span className="font-medium">
                        Pros:
                      </span>{" "}
                      {alternative.pros}
                    </p>
                  )}

                  {alternative.cons && (
                    <p>
                      <span className="font-medium">
                        Cons:
                      </span>{" "}
                      {alternative.cons}
                    </p>
                  )}

                </div>

              </div>
            );
          }
        )}

      </div>

      {/* COMPARISON TABLE */}

      {selectedAlternatives.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">

          <h2 className="mb-4 text-xl font-semibold text-gray-800">
            Comparison Table
          </h2>

          <p className="mb-4 text-sm text-gray-600">
            Comparing{" "}
            {selectedAlternatives.length}{" "}
            alternative
            {selectedAlternatives.length > 1
              ? "s"
              : ""}
            .
          </p>

          <div className="overflow-x-auto">

            <table className="min-w-full border-collapse text-left text-sm">

              <thead>

                <tr className="bg-gray-100">

                  <th className="border p-3">
                    Property
                  </th>

                  {selectedAlternatives.map(
                    (alternative) => (
                      <th
                        key={
                          alternative.id
                        }
                        className="border p-3"
                      >
                        {alternative.title ||
                          alternative.name ||
                          `Alternative ${alternative.id}`}
                      </th>
                    )
                  )}

                </tr>

              </thead>

              <tbody>

                {/* DESCRIPTION */}

                <tr>

                  <td className="border p-3 font-medium">
                    Description
                  </td>

                  {selectedAlternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                        className="border p-3"
                      >
                        {alternative.description ||
                          "N/A"}
                      </td>
                    )
                  )}

                </tr>

                {/* COST */}

                <tr>

                  <td className="border p-3 font-medium">
                    Cost
                  </td>

                  {selectedAlternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                        className="border p-3"
                      >
                        {alternative.cost ??
                          alternative.estimated_cost ??
                          "N/A"}
                      </td>
                    )
                  )}

                </tr>

                {/* BENEFIT */}

                <tr>

                  <td className="border p-3 font-medium">
                    Benefit
                  </td>

                  {selectedAlternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                        className="border p-3"
                      >
                        {alternative.benefit ??
                          "N/A"}
                      </td>
                    )
                  )}

                </tr>

                {/* RISK */}

                <tr>

                  <td className="border p-3 font-medium">
                    Risk
                  </td>

                  {selectedAlternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                        className="border p-3"
                      >
                        {alternative.risk_level ||
                          alternative.risk ||
                          "N/A"}
                      </td>
                    )
                  )}

                </tr>

                {/* SCORE */}

                <tr>

                  <td className="border p-3 font-medium">
                    Score
                  </td>

                  {selectedAlternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                        className="border p-3"
                      >
                        {alternative.score ??
                          alternative.feasibility_score ??
                          "N/A"}
                      </td>
                    )
                  )}

                </tr>

                {/* PROS */}

                <tr>

                  <td className="border p-3 font-medium">
                    Pros
                  </td>

                  {selectedAlternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                        className="border p-3"
                      >
                        {alternative.pros ||
                          "N/A"}
                      </td>
                    )
                  )}

                </tr>

                {/* CONS */}

                <tr>

                  <td className="border p-3 font-medium">
                    Cons
                  </td>

                  {selectedAlternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                        className="border p-3"
                      >
                        {alternative.cons ||
                          "N/A"}
                      </td>
                    )
                  )}

                </tr>

              </tbody>

            </table>

          </div>

        </div>
      )}

    </div>
  );
};

export default AlternativeComparison;