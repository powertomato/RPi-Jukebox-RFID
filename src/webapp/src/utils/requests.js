import { socketRequest } from "../sockets";

const getFlattenListOfDirectories = async () => {
  const list = await socketRequest('player', 'ctrl', 'list_all_dirs');
  return list.filter(entry => !!entry.directory);
};

const fetchCardsList = async (setIsLoading) => {
  setIsLoading(true);

  try {
    const result = await socketRequest('cards', 'list_cards');
    setIsLoading(false);
    return { result };
  }
  catch (error) {
    console.error('registerCard error: ', error);
    setIsLoading(false);
    return { error };
  };
};

const registerCard = async (kwargs) => {
  try {
    const result = await socketRequest('cards', 'register_card', null, kwargs);
    return { result };
  }
  catch (error) {
    console.error('registerCard error: ', error);
    return { error };
  }
};

const deleteCard = async (card_id) => {
  try {
    const result = await socketRequest('cards', 'delete_card', null, { card_id: card_id.toString() });
    return { result };
  }
  catch (error) {
    return { error };
  }
};

export {
  getFlattenListOfDirectories,
  fetchCardsList,
  deleteCard,
  registerCard,
}