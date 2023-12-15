<template>
  <b-container class="my-4">
    <b-row>
      <b-col>
        <h1 class="mb-4">Flashcard Decks</h1>
        <b-input-group class="mb-3">
          <b-form-input placeholder="Search for a deck..."></b-form-input>
          <b-input-group-append>
            <b-button variant="outline-secondary">Search</b-button>
          </b-input-group-append>
        </b-input-group>
        <b-list-group>
          <b-list-group-item 
            v-for="deck in decks" 
            :key="deck.id" 
            class="d-flex justify-content-between align-items-center">
            {{ deck.name }}
            <div class="deck-stats">
                <span>{{ deck.numCards }} cards</span>
                <span>{{ deck.percentComplete }}% complete</span>
                <span>{{ deck.hoursStudied }} hours studied</span>
                <span>      <b-progress :value="deck.percentComplete" :max="100"></b-progress>
                </span>
              </div>
            <b-button-group>
              <b-button variant="info" size="sm">Edit</b-button>
              <b-button variant="danger" size="sm">Delete</b-button>
            </b-button-group>
          </b-list-group-item>
        </b-list-group>
        <b-button variant="primary" class="mt-3" @click="addDeck">+ Add Deck</b-button>
      </b-col>
    </b-row>
  </b-container>
</template>

<script>
export default {
  data() {
    return {
      decks: [

      { id: 1, name: "Deck 1", numCards: 50, percentComplete: 80, hoursStudied: 5 },
        { id: 2, name: "Deck 2", numCards: 30, percentComplete: 60, hoursStudied: 3 },
 
        // Add more decks as needed
      ]
    };
  },
  methods: {
    addDeck() {
      const newDeckId = this.decks.length + 1;
      this.decks.push({ id: newDeckId, name: `Deck ${newDeckId}` });
    }
  }
};
</script>

  
<style scoped>
  /* General Styles */
  h1 {
    font-size: 2rem; /* Larger title */
    color: #343a40; /* Bootstrap's default dark color */
    text-align: center;
    margin-bottom: 1rem;
  }
  
  /* Search Bar Styles */
  .input-group {
    margin-bottom: 1.5rem;
  }
  
  .form-input {
    border-radius: 0.25rem;
  }
  
  /* List Group Item Styles */
  .list-group-item {
    background-color: #f8f9fa; /* Lighter background */
    border: 1px solid #e9ecef; /* Subtle border */
    border-radius: 0.25rem; /* Rounded corners */
    transition: background-color 0.3s, box-shadow 0.3s; /* Smooth transition for hover effect */
  }
  
  .list-group-item:hover {
    background-color: #e2e6ea; /* Slightly darker on hover */
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* Soft shadow for depth */
  }
  
  /* Button Styles */
  .button {
    margin-left: 0.5rem; /* Spacing between buttons */
  }
  
  .add-button {
    background-color: #007bff; /* Primary blue */
    color: white;
    padding: 0.5rem 1rem; /* Padding for larger clickable area */
    border-radius: 0.25rem; /* Rounded corners */
    transition: background-color 0.3s; /* Smooth transition for hover effect */
  }
  
  .add-button:hover {
    background-color: #0056b3; /* Darker blue on hover */
  }

  .deck-stats {
    display: flex;
    justify-content: space-between;
    font-size: 0.9em;
    width: 100%; /* Full width */

  }
  .deck-stats span {
    margin-right: 10px;
  }
  


  .deck-stats {
    /* ... */
    width: 100%; /* Full width */
  }

  .progress {
    height: 1em; /* Smaller height */
    margin-top: 0.5rem; /* Spacing from the top */
    width: 100px; /* Full width */

  }
  /* ... */
  </style>
  