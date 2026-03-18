defmodule Orchestrator.Pipeline.Step do
  @moduledoc """
  Defines a pipeline step behaviour and struct.

  Each step receives a context map, performs its action, and returns
  an updated context or an error.
  """

  @callback execute(context :: map()) :: {:ok, map()} | {:error, String.t()}

  defstruct [:name, :module, :function, args: []]

  @type t :: %__MODULE__{
          name: String.t(),
          module: module(),
          function: atom(),
          args: list()
        }

  @doc """
  Execute a step by calling its module/function with the given context.
  """
  @spec execute(t(), map()) :: {:ok, map()} | {:error, String.t()}
  def execute(%__MODULE__{module: module, function: function, args: args}, context) do
    apply(module, function, [context | args])
  end
end
