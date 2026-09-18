const LoadingState = ({
  message = "Loading, please wait...",
}) => {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg bg-gray-50 px-6 py-12 text-center">
      <div className="h-10 w-10 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600"></div>

      <p className="mt-4 text-sm text-gray-600">
        {message}
      </p>
    </div>
  );
};

export default LoadingState;