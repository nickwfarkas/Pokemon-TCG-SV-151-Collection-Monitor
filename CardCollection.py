import pandas as pd
import requests

class CardCollection:
    __main_df = None
    __tcgplayer_df = None
    __collection_df = None
    __api_url = ""
    __x_api_key = ""
    __path_to_collection = ""
    __header = {}
    __outstanding_df = None
    __owned_df = None

    def __init__(self,
                 x_api_key,
                 path_to_collection="C:\\Program Files\\PokemonInventory\\application\\Pokemon151Inventory.xlsx",
                 api_url = "https://api.pokemontcg.io/v2/cards?q=set.id:sv3pt5&pageSize=207&select=id,name,number,rarity,tcgplayer") -> None:
        self.__api_url = api_url
        self.__x_api_key = x_api_key
        self.__path_to_collection = path_to_collection
        self.__initialize_collection()
        self.__set_header()
        self.__set_tcg_player_data()
        self.__set_main()
        self.__set_outstanding()
        self.__set_owned()

    def __initialize_collection(self):
        try:
            self.__collection_df = pd.read_excel(self.__path_to_collection)
        except FileNotFoundError as e:
            self.__collection_df = None
            print(f"No collection found at: {self.__path_to_collection}")
        except Exception as e:
            self.__collection_df = None
            print(e)
    
    def __set_header(self):
        if(self.__x_api_key):
            self.__header = {
                'X-Api-Key': self.__x_api_key
            }

    def __tcg_player_req(self):
        try:
            print("Requesting TCG Player Data...")
            response = requests.get(self.__api_url, headers=self.__header)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        except Exception as e:
            print(e)

    def __clean_tcg_player_data(self):
        try:
            market_price_atr = [col for col in self.__tcgplayer_df.columns if 'market' in col.lower()]
            self.__tcgplayer_df["MP"] = self.__tcgplayer_df[market_price_atr].median(axis=1,skipna=True)
            self.__tcgplayer_df["Market Price"] = self.__tcgplayer_df["MP"].apply(lambda x: "${:.2f}".format(x))
            self.__tcgplayer_df = self.__tcgplayer_df.rename(columns={"number":"ID","name":"Card Name","rarity":"Rarity","tcgplayer_url":"TCG Player URL"})
            self.__tcgplayer_df["ID"] = self.__tcgplayer_df["ID"].astype('int64')
            print("TCG Player Recieved!")
        except Exception as e:
            print(f'Failed while cleaning tcgplayer data: {e}')

    def __set_tcg_player_data(self):
        if(not self.__collection_df.empty and self.__header):
            response = self.__tcg_player_req()
            if(response):
                self.__tcgplayer_df = pd.json_normalize(response['data'], sep='_')
                self.__clean_tcg_player_data()

    def __set_main(self):
        if(not self.__collection_df.empty and not self.__tcgplayer_df.empty):
            self.__main_df = pd.merge(self.__tcgplayer_df, self.__collection_df, how="left", on='ID')
    
    def raw_to_csv(self, file_name = "Pokemon151InventoryMarketPrices.csv"):
        print("Exporting...")
        self.__main_df.to_csv(file_name,index=False)
        print(f"Exported as {file_name}!")

    def owned_breakdown_to_csv(self, file_name = "Pokemon151InventoryOwnedBreakdown.csv"):
        print("Exporting...")
        self.get_owned_price_breakdown_df().to_csv(file_name,index=False)
        print(f"Exported as {file_name}!")
    
    def outstanding_breakdown_to_csv(self, file_name = "Pokemon151InventoryOutstandingBreakdown.csv"):
        print("Exporting...")
        self.get_outstanding_price_breakdown_df().to_csv(file_name,index=False)
        print(f"Exported as {file_name}!")

    def __set_outstanding(self):
        if(not self.__main_df.empty):
            self.__outstanding_df = self.__main_df[self.__main_df['Count'] < 1]
    
    def __set_owned(self):
        if(not self.__main_df.empty):
            self.__owned_df = self.__main_df[self.__main_df['Count'] > 0]

    def get_n_outstanding(self):
        if(not self.__outstanding_df.empty):
            return self.__outstanding_df.shape[0]

    def get_n_owned(self):
        if(not self.__owned_df.empty):
            return self.__owned_df.shape[0]
        
    def get_outstanding_price_breakdown_df(self):
        if(not self.__outstanding_df.empty):
            breakdown_atr = ['ID','Card Name','Rarity',"Market Price"]
            return self.__outstanding_df[breakdown_atr]
        
    def get_owned_price_breakdown_df(self):
        if(not self.__owned_df.empty):
            breakdown_atr = ['ID','Card Name','Rarity',"Market Price"]
            return self.__owned_df[breakdown_atr]
    
    def get_outstanding_MP(self):
        if(not self.__outstanding_df.empty):
            return "${:.2f}".format(self.__outstanding_df["MP"].sum())
        
    def get_owned_MP(self):
        if(not self.__owned_df.empty):
            return "${:.2f}".format(self.__owned_df["MP"].sum())
        
    def get_n(self):
        return f"Cards Owned: {self.get_n_owned()}\nCards Oustanding: {self.get_n_outstanding()}"
    
    def get_MP(self):
        return f"Cards Owned Market Price: {self.get_owned_MP()}\nCards Oustanding Market Price: {self.get_outstanding_MP()}"
    








    