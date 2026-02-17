import lib.data as dataConventer
import lib.prompt as promptGenerator
import lib.LLMRequests as LLM
import pandas as pd

def generatePromptFromExcel(file_path: str) -> str:
    df = pd.read_excel(file_path)

    profile = dataConventer.profileDataframe(df)

    sample_rows = df.head(6)


    userPrompt = promptGenerator.userPrompt(profile, sample_rows)
    systemPrompt = promptGenerator.systemPrompt()
    print("==== Prompt ====")
    print(userPrompt)
    print(systemPrompt)
    lst = LLM.GetLLMResponse(userPrompt, systemPrompt, debugMessages=True)

def main():
    generatePromptFromExcel("testTable.xlsx")


if __name__ == "__main__":
    main()