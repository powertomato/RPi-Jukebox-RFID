import React, { useEffect, useState } from 'react';
import { useHistory, useParams } from 'react-router';

import Avatar from '@material-ui/core/Avatar';
import BookmarkIcon from '@material-ui/icons/Bookmark';
import Button from '@material-ui/core/Button';
import Card from '@material-ui/core/Card';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardHeader from '@material-ui/core/CardHeader';
import CircularProgress from '@material-ui/core/CircularProgress';
import Grid from '@material-ui/core/Grid';

import Header from '../Header';
import ControlsSelector from './controls/controls-selector';
import CardsDeleteDialog from './dialogs/delete';
import { fetchCardsList, deleteCard, registerCard } from '../../utils/requests';

const CardEdit = () => {
  const history = useHistory();
  const params = useParams();
  const { location: { state } } = history;

  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [cardId, setCardId] = useState(undefined);
  const [selectedAction, setSelectedAction] = useState(undefined);
  const [selectedFolder, setSelectedFolder] = useState(undefined);
  const [isLoading, setIsLoading] = useState(false);

  const handleRegisterCard = async (card_id) => {
    const kwargs = {
      card_id: card_id.toString(),
      quick_select: selectedAction,
      overwrite: true,
    };

    if (selectedAction === 'play_card') {
      kwargs.args = selectedFolder;
    }

    const { error } = await registerCard(kwargs);

    if (error) {
      return console.error(error);
    }

    history.push('/cards');
  };

  const handleDeleteCard = async () => {
    const { error } = await deleteCard(cardId);

    if (error) {
      return console.error(error);
    }

    history.push('/cards');
  };

  useEffect(() => {
    if (state && state.id) {
      setCardId(state.id);
      setSelectedAction(state.from_quick_select);
      setSelectedFolder(state.action?.args);
      return;
    }

    const loadCardList = async () => {
      const { result, error } = await fetchCardsList(setIsLoading);

      if (result && params?.cardId && result[params.cardId]) {
        setCardId(params.cardId);
        setSelectedAction(result[params.cardId].from_quick_select);
        setSelectedFolder(result[params.cardId].action?.args);
      }

      if (error) {
        console.error(error);
        history.push('/cards');
      }
    }

    loadCardList();
  }, [history, params, state]);

  return (
    <>
      <Header title="Edit Card" backLink="/cards" />
      <Grid container>
        <Grid item xs={12}>
          <Card elevation={0}>
            <CardHeader
              avatar={
                <Avatar aria-label="Card Icon">
                  <BookmarkIcon />
                </Avatar>
              }
              title={cardId}
            />
            <CardContent>
              {isLoading
                ? <CircularProgress />
                : <Grid container direction="row" alignItems="center">
                    <ControlsSelector
                      selectedAction={selectedAction}
                      setSelectedAction={setSelectedAction}
                      selectedFolder={selectedFolder}
                      setSelectedFolder={setSelectedFolder}
                    />
                  </Grid>
              }
            </CardContent>
            <CardActions>
              <Button
                color="secondary"
                size="small"
                onClick={(e) => setDeleteDialogOpen(true)}
              >
                Delete
              </Button>
              <Button
                size="small"
                color="primary"
                onClick={(e) => handleRegisterCard(cardId)}
              >
                Save
              </Button>
            </CardActions>
          </Card>
        </Grid>
      </Grid>
      <CardsDeleteDialog
        open={deleteDialogOpen}
        onClose={() => setDeleteDialogOpen(false)}
        doDelete={handleDeleteCard}
        cardId={cardId}
      />
    </>
  );
};

export default CardEdit;